import re

from command_collector import *
from latex_command import LatexCommand


def substitute_command(content, command):
    result = content
    name_len = len(command.name)
    pattern = f"(?<!newcommand{{){re.escape(command.name)}(?![a-zA-Z])"
    compiled = re.compile(pattern)
    
    position = 0
    while True:
        match = compiled.search(result, position)
        if not match:
            break
        command_pos = match.start()
        position = command_pos + name_len

        params = []
        for i in range(command.num_params):
            if result[position] != '{':
                raise ValueError(f"Incorrect content: didn't find needed parameters in command {command.name}.")
            p = get_command_designation(result, position)
            position += len(p) + 2
            params.append(p)

        full_command = command.substitute_params(params)
        result = result.replace(result[command_pos:position], full_command)
        position = command_pos + len(full_command) - 1

    return result


def find_first_comment_position(content):
    match = re.search(r'(?<!\\)%', content)
    return match.start() if match else -1


def find_first_line_end_position(content):
    match = re.search(r'(?<!\\)(?:\\{2})*(?:\r?\n)', content)
    return match.end() if match else -1


def sty_to_commands(sty_file: str):
    with open(sty_file, 'r', encoding='utf-8') as file:
        content = file.read()

    commands = []

