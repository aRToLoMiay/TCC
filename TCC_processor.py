from command_collector import *
from text_fragment import *

import os
import re


class TccProcessor:
    def __init__(self, tex_files_list, sty_files_list = []):
        self.texs = tex_files_list
        self.stys = sty_files_list
        self._file = ""
        self._commands = {}
        self._fragments = []


    def process_tex(self, tex_file):
        # Class prepararion.
        self._clear()
        self._file = tex_file

        # Get content from file.
        try:
            with open(tex_file, 'r', encoding='utf-8') as file:
                content = file.read()
                self._fragments.append(TextFragment(content=content, 
                                                   tex_file_path=self._file))
        except Exception as e:
            print(f"Error : File {self._file} cannot open.")
            return

        # Process file content.
        self._separate_comments()
        self._clear_empty_fragments()
        # <--- Add include{tex} fragments. Recursive?
        self._extract_sty_commands()
        self._extract_newcommands()
        self._unite_empty_fragments()
        self._expand_commands()

        # Result collection.
        result = self._collect_content()
        return result
        
    # ----------------------------------------
    # Functional methods.
    # ----------------------------------------

    def _clear(self):
        self._commands = {}
        self._fragments.clear()

    # ----------------------------------------
    # Main processor methods.
    # ----------------------------------------
    def _separate_comments(self):
        i = 0
        comment_before = False
        while True:
            match = re.search(r'(?<!\\)%', self._fragments[i].content)
            if not match:
                break
            pos = match.start()
        
            comment_fragment = self._fragments[i].separate_tail(pos)
            comment_fragment.without_rules = True
            if pos == 0:
                comment_before = True
            else:
                comment_before = False
                self._fragments.append(comment_fragment)
                i += 1
        
            match = re.search(r'(?<!\\)(?:\\{2})*(?:\r?\n)', comment_fragment.content)
            if not match:
                break
            pos = match.start()
        
            after_comment_fragment = comment_fragment.separate_tail(pos)
            after_comment_fragment.without_rules = False

            if comment_before:
                self._fragments[i-1].append(comment_fragment)
                self._fragments[i].content = after_comment_fragment.content
            else:
                self._fragments.append(after_comment_fragment)
                i += 1


    def _clear_empty_fragments(self):
        for fragment in self._fragments:
            if fragment.without_rules:
                continue
            if fragment.is_blank():
                fragment.without_rules = True

    
    def _extract_sty_commands(self):
        for sty in self.stys:
            sty_str = self._sty_path_to_usepackage(sty)
            pattern = re.escape("\\usepackage{" + sty_str + "}")

            i = 0
            n = len(self._fragments)
            while i < n:
                fragment = self._fragments[i]
                if fragment.without_rules:
                    i += 1
                    continue
                result = re.search(pattern, fragment.content)
                if result == None:
                    i += 1
                    continue
            
                # Split fragment with usepackage to the parts.
                sty_fragment = fragment.separate_tail(result.start())
                after_sty_fragment = sty_fragment.separate_tail(len(pattern))
                sty_fragment.without_rules = True
                self._fragments.insert(i + 1, after_sty_fragment)
                self._fragments.insert(i + 1, sty_fragment)
                i += 2
                n += 2

                command = None
                with open(sty, 'r', encoding='utf-8') as file:
                    content = file.read()
                    commands = extract_commands_declarations(content)

                self._setup_rules(i, commands)
                for cmd in commands:
                    self._commands[cmd.id] = cmd


    def _extract_newcommands(self):
        i = 0
        n = len(self._fragments)
        while i < n:
            fragment = self._fragments[i]
            position = 0
            while True:
                c, position, start = extract_next_command_declaration(fragment.content, position)
                if not position:
                    break
                if c:

                    # Fragmentation of fragment by command definition.
                    cmd_fragment = fragment.separate_tail(start - 1)
                    after_sty_fragment = cmd_fragment.separate_tail(position - start + 1)
                    cmd_fragment.without_rules = True
                    self._fragments.insert(i + 1, after_sty_fragment)
                    self._fragments.insert(i + 1, cmd_fragment)
                    i += 1
                    n += 2
                    self._setup_rules(i, [c])
                    self._commands[c.id] = c

                    # Check existing command and update existing rules.
                    if c.command != "renewcommand":
                        continue
                    is_overlap, overlap_list = self._is_command_in_rules(fragment, c)
                    if is_overlap:
                        self._remove_rules(i, overlap_list)
            i += 1


    def _unite_empty_fragments(self):
        self._clear_empty_fragments()
        i = 0
        n = len(self._fragments)
        while i < n - 1:
            fragment = self._fragments[i]
            if fragment.without_rules:
                fragment.active_rules = []
                while True:
                    next_fragment = self._fragments[i + 1]
                    if not next_fragment.without_rules:
                        break
                    if fragment.tex_file_path != next_fragment.tex_file_path:
                        break
                    fragment.append(next_fragment)
                    self._fragments.pop(i+1)
                    n -= 1
                    if i == n - 1:
                        break
            i += 1


    def _expand_commands(self):
        for fragment in self._fragments:
            if fragment.without_rules:
                continue
            for cmd_id in fragment.active_rules:
                fragment.content = self._expand_command(fragment.content, 
                                                        self._commands.get(cmd_id))

    # ----------------------------------------
    # Auxiliary processor methods.
    # ----------------------------------------

    def _sty_path_to_usepackage(self, sty_path: str) -> str:
        """
        Convert path to sty-file into usepackage view.
        """
        sty_path = os.path.normpath(sty_path)
        tex_path = os.path.normpath(self._file)
    
        sty_parts = sty_path.split(os.sep)
        tex_parts = tex_path.split(os.sep)
    
        common_parts = []
        for p1, p2 in zip(sty_parts, tex_parts):
            if p1 == p2:
                common_parts.append(p1)
            else:
                break
    
        if not common_parts:
            result = sty_path
        else:
            result_parts = sty_parts[len(common_parts):]
            result = os.path.join(*result_parts)
    
        result = result.replace("\\", "/")
        result = result.replace(".sty", "")
        return result


    def _setup_rules(self, position, rules):
        for i in range(position, len(self._fragments)):
            fragment = self._fragments[i]
            if fragment.without_rules:
                continue
            for rule in rules:
                fragment.add_rule(rule.id)


    def _remove_rules(self, position, rules_list):
        for i in range(position, len(self._fragments)):
            fragment = self._fragments[i]
            for rule in rules_list:
                fragment.remove_rule(rule)


    def _is_command_in_rules(self, fragment, command):
        overlap_list = []
        for i in fragment.active_rules:
            if command.name == self._commands[i].name:
                overlap_list.append(i)
        return (len(overlap_list) != 0), overlap_list


    def _expand_command(self, content, command):
        pattern = re.escape(command.name)
        compiled = re.compile(pattern)

        try:
            position = 0
            while True:
                cmd_name, cmd_impl, position = extract_next_command(content, position, command)
                if cmd_name == None:
                    break
                content = content.replace(cmd_name, cmd_impl, 1)
                position += len(cmd_impl) - len(cmd_name)
                if position >= len(content):
                    break
        except Exception as e:
            print(e)

        return content


    def _collect_content(self):
        return "".join(f.content for f in self._fragments)
    
    # ----------------------------------------
    # Testing methods.
    # ----------------------------------------
    
    def _print_fragment_by_framgent(self, skip_without_rules: bool = False):
        import os
        i = 0
        for fragment in self._fragments:
            if not (skip_without_rules and fragment.without_rules):
                print(f"Framgnet [{i}]")
                print(f"--- Is rules active   : {not fragment.without_rules}")
                print(f"--- Active rules list : {fragment.active_rules}")
                print(f"--- Content           :")
                print(repr(fragment.content))
                print("---")
                input("Press Enter...")
                os.system('cls')
            i += 1
