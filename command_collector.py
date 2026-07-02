from latex_command import *

import re

__all__ = [
    'extract_commands_declarations',
    'extract_next_command_declaration',
    'extract_next_command',
]

# --------------------------------------------------------------------------------
# Main extract methods.
# --------------------------------------------------------------------------------

def extract_commands_declarations(content):
    commands = []
    position = 0
    while True:
        c, position, start = extract_next_command_declaration(content, position)
        if not position:
            break
        if c:
            commands.append(c)
    return commands


def extract_next_command_declaration(content, position):
    try:
        start, position, cmd = _find_next_command_pos(content, position)
        if not position:
            return None, None, None

        name = _get_command_designation(content, position)
        position += len(name) + 2
        count, position = _get_parameters_count(content, position)
        default, position = _get_default_value(content, position)
        signature = _get_command_designation(content, position)
        position += len(signature) + 2
        
        c = LatexCommand(command=cmd, 
                         name=name, 
                         num_params=count, 
                         implementation=signature, 
                         default_value=default)
    except Exception as e:
        if name:
            print(f"Problem with extraction of command {name}: {e}")
        else:
            print(f"Problem with extraction of command: {e}")
        position += 1
        return None, position, start
    return c, position, start


def extract_next_command(content, position, command):
    pattern = re.escape(command.name)
    compiled = re.compile(pattern)
    match = compiled.search(content, position)
    if not match:
        return None, None, position
    position = match.end()

    if command.num_params == 0:
        cmd_name = command.name
        cmd_impl = command.substitute_params()
        return cmd_name, cmd_impl, match.start()

    if command.num_params == 1 and command.default_value != None:
        cmd_name = command.name
        cmd_impl = command.substitute_params()
        return cmd_name, cmd_impl, match.start()

    if content[match.end()] != '{':
        raise ValueError(f"Cannot find parameters of command {command.name} in text.")
    
    cmd_params = []
    iter_count = command.num_params
    if command.default_value != None:
        iter_count -= 1
    for i in range(0, iter_count):
        if content[position] != '{':
            raise ValueError(f"Cannot find parameters for command {command.name} in text.")
        cmd_params.append(_get_command_designation(content, position))
        position += len(cmd_params[-1]) + 2
    cmd_name = content[match.start():position + 1]
    cmd_impl = command.substitute_params(cmd_params)

    return cmd_name, cmd_impl, match.start()

# --------------------------------------------------------------------------------
# Additional methods.
# --------------------------------------------------------------------------------

def _find_next_command_pos(content, position=0):
    words = ["newcommand", "renewcommand", "providecommand", "DeclareRobustCommand"]
    pattern = '|'.join(re.escape(word) for word in words)
    compiled = re.compile(pattern)
    match = compiled.search(content, position)
    if match:
        return match.start(), match.end(), match.group(0)
    else:
        return None, None, None


def _next_word_pos(content, word, position=0):
    compiled = re.compile(word)
    match = compiled.search(content, position).end()
    return match if match else -1


def _get_parameters_count(content, position):
    if content[position] != '[':
        return 0, position
    pattern = re.compile(re.escape(']'))
    match = pattern.search(content, pos=position).end()
    if match == -1:
        raise ValueError("Incorrect content: didn't find close ']' symbol in command.")
    return int(content[position + 1:match - 1]), match


def _get_default_value(content, position):
    if content[position] != '[':
        return None, position
    pattern = re.compile(re.escape(']'))
    match = pattern.search(content, pos=position).end()
    if match == -1:
        raise ValueError("Incorrect content: didn't find close ']' symbol in command.")
    return content[position + 1:match - 1], match


def _get_command_designation(content, position):
    compiled = re.compile(r'[{}]')
    match = compiled.search(content, pos=position).end()

    counter = 1
    pos = position + 1
    while counter > 0:
        match = compiled.search(content, pos=pos)
        if not match:
            raise ValueError("Incorrect content: didn't find close '}' symbol in command.")
        match = match.end()
        if _is_ecranned(content, match):
            continue
        if content[match - 1] == '{':
            counter = counter + 1
        else:
            counter = counter - 1
        pos = match
    return content[position + 1:pos - 1]


def _is_ecranned(content, position):
    count = 0
    pos = position - 1
    while content[pos] == '\\' and pos >= 0:
        count += 1
        pos -= 1
    return count % 2 == 1
