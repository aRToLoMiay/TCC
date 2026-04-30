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