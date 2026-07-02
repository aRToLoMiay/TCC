from path_processor import *
from console_menu import *

from latex_dd import collect_files
from text_fragment import TextFragment, collect_fragments_content
from tex_analyzer import find_first_comment_position, find_first_line_end_position
from command_collector import extract_commands_declarations, extract_next_command_declaration, extract_next_command

import os
import re

selected_file = None
d_commands = {}


def print_fragment_by_framgent(fragments, skip_without_rules: bool = False):
    i = 0
    for fragment in fragments:
        if not (skip_without_rules and fragment.without_rules):
            print(f"--- {i}")
            print(f"--- Rules active = {not fragment.without_rules}")
            print(f"--- active_rules = {fragment.active_rules}")
            print(repr(fragment.content))
            print("---")
            input("Press Enter...")
            os.system('cls')
        i += 1


def result_to_file(fragments, skip_without_rules: bool = False):
    print(f"Nomuber of fragments: {len(fragments)}")
    text = collect_fragments_content(fragments, skip_without_rules)
    with open('result.tex', 'w', encoding='utf-8') as file:
        file.write(text)


def sty_path_to_usepackage(sty_path: str, tex_path: str) -> str:
    """
    Преобразуем путь к sty-файлу в вид, используемый в usepackage внутри tex-файла.
    tex_path используется для отсечения пути в случае, если tex-файл находится в поддиректории.
    """
    sty_path = os.path.normpath(sty_path)
    tex_path = os.path.normpath(tex_path)
    
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


def make_option_handler(text):
    def handler():
        global selected_file
        selected_file = text
    return handler


def separate_comments(started_fragment):
    fragments = []
    fragments.append(started_fragment)
    i = 0
    comment_before = False
    while True:
        pos = find_first_comment_position(fragments[i].content)
        if pos == -1:
            break
        
        comment_fragment = fragments[i].separate_tail(pos)
        comment_fragment.without_rules = True
        if pos == 0:
            comment_before = True
        else:
            comment_before = False
            fragments.append(comment_fragment)
            i += 1
        
        pos = find_first_line_end_position(comment_fragment.content)
        if pos == -1:
            break
        
        after_comment_fragment = comment_fragment.separate_tail(pos)
        after_comment_fragment.without_rules = False

        if comment_before:
            fragments[i-1].append(comment_fragment)
            fragments[i].content = after_comment_fragment.content
        else:
            fragments.append(after_comment_fragment)
            i += 1
    return fragments


def clear_empty(fragments):
    for fragment in fragments:
        if fragment.without_rules:
            continue
        if fragment.is_blank():
            fragment.without_rules = True
    return fragments


def unite_empty(fragments):
    clear_empty(fragments)
    i = 0
    n = len(fragments)
    while i < n - 1:
        fragment = fragments[i]
        if fragment.without_rules:
            fragment.active_rules = []
            while True:
                next_fragment = fragments[i + 1]
                if not next_fragment.without_rules:
                    break
                if fragment.tex_file_path != next_fragment.tex_file_path:
                    break
                fragment.append(next_fragment)
                fragments.pop(i+1)
                n -= 1
                if i == n - 1:
                    break
        i += 1
    return fragments


def setup_rules(fragments, pos, rules):
    for i in range(pos, len(fragments)):
        fragment = fragments[i]
        if fragment.without_rules:
            continue
        for rule in rules:
            fragment.add_rule(rule.id)


def extract_sty_commands(fragments, sty_files, tex_file):
    for sty in sty_files:
        sty_str = sty_path_to_usepackage(sty, tex_file)
        pattern = re.escape("\\usepackage{" + sty_str + "}")

        i = 0
        n = len(fragments)
        while i < n:
            fragment = fragments[i]
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
            fragments.insert(i + 1, after_sty_fragment)
            fragments.insert(i + 1, sty_fragment)
            i += 2
            n += 2

            command = None
            with open(sty, 'r', encoding='utf-8') as file:
                content = file.read()
                commands = extract_commands_declarations(content)

            setup_rules(fragments, i, commands)
            for cmd in commands:
                d_commands[cmd.id] = cmd

    return fragments


def is_command_in_rules(fragment, command):
    overlap_list = []
    for i in fragment.active_rules:
        if command.name == d_commands[i].name:
            overlap_list.append(i)
    return (len(overlap_list) != 0), overlap_list


def remove_rules(fragments, position, rules_list):
    for i in range(position, len(fragments)):
        fragment = fragments[i]
        for rule in rules_list:
            fragment.remove_rule(rule)


def extract_newcommands(fragments):
    i = 0
    n = len(fragments)
    while i < n:
        fragment = fragments[i]
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
                fragments.insert(i + 1, after_sty_fragment)
                fragments.insert(i + 1, cmd_fragment)
                i += 1
                n += 2
                setup_rules(fragments, i, [c])
                d_commands[c.id] = c

                # Check existing command and update existing rules.
                if c.command != "renewcommand":
                    continue
                is_overlap, overlap_list = is_command_in_rules(fragment, c)
                if is_overlap:
                    remove_rules(fragments, i, overlap_list)
                
        i += 1
    return fragments


def expand_commands(fragments):
    for fragment in fragments:
        if fragment.without_rules:
            continue
        for cmd_id in fragment.active_rules:
            fragment.content = expand_command(fragment.content, d_commands.get(cmd_id))
    return fragments


def expand_command(content, command):
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


def get_file():
    selected_file = "TestTex\main.tex"

    # Get files list.
    tex_files = collect_files('.tex')
    sty_files = collect_files('.sty')

    # # Select processing file.
    # main_menu = Menu("Choose file fore processing:")
    # for path in tex_files:
    #     main_menu.add_action_item(path,make_option_handler(path))
    # main_menu.run()
    # os.system('cls')
    
    # Get file content.
    with open(selected_file, 'r', encoding='utf-8') as file:
        content = file.read()
    
    fragments = separate_comments(TextFragment(content, selected_file))
    fragments = clear_empty(fragments)
    # <--- Add include{tex} fragments. Recursive?
    fragments = extract_sty_commands(fragments, sty_files, selected_file)
    fragments = extract_newcommands(fragments)
    fragments = unite_empty(fragments)
    fragments = expand_commands(fragments)
    
    # for key in d_commands.keys():
    #     print(f"[{key}] : {d_commands[key].name}")
    # print(fragments[-1].content)
    print(collect_fragments_content(fragments))
    # print_fragment_by_framgent(fragments, False)
    # result_to_file(fragments, True)


if __name__ == "__main__":
    get_file()
