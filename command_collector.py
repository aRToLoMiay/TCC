import re

from latex_command import LatexCommand


def find_next_command_pos(content, position=0):
    words = ["newcommand", "renewcommand"]
    pattern = '|'.join(re.escape(word) for word in words)
    compiled = re.compile(pattern)
    match = compiled.search(content, position)
    return match.end() if match else -1


def next_word_pos(content, word, position=0):
    compiled = re.compile(word)
    match = compiled.search(content, position).end()
    return match if match else -1

def get_parameters_count(content, position):
    if content[position] != '[':
        return 0, position
    pattern = re.compile(re.escape(']'))
    match = pattern.search(content, pos=position).end()
    if match == -1:
        raise ValueError("Incorrect content: didn't find close ']' symbol in command.")
    return int(content[position + 1:match - 1]), match


def get_command_designation(content, position):
    compiled = re.compile(r'[{}]')
    match = compiled.search(content, pos=position).end()

    counter = 1
    pos = position + 1
    while counter > 0:
        match = compiled.search(content, pos=pos).end()
        if is_ecranned(content, match):
            continue
        if content[match - 1] == '{':
            counter = counter + 1
        else:
            counter = counter - 1
        pos = match
        if match == -1:
            raise ValueError("Incorrect content: didn't find close '}' symbol in command.")
    return content[position + 1:pos - 1]


def is_ecranned(content, position):
    count = 0
    pos = position - 1
    while content[pos] == '\\' and pos >= 0:
        count += 1
        pos -= 1
    return count % 2 == 1


def extract_commands(content):
    commands = []
    position = 0

    while True:
        position = find_next_command_pos(content, position)
        if position == -1:
            break

        name = get_command_designation(content, position)
        position += len(name) + 2
        count, position = get_parameters_count(content, position)
        signature = get_command_designation(content, position)
        position += len(signature) + 2
        
        c = LatexCommand(name, signature, count)
        commands.append(c)

    for command in commands:
        print(command.get_tex_str())
    return commands


def substitute_command(content, command):
    position = 0
    # position = next_word_pos(content, command, position)
    # print(position)

    pattern = f"(?<!newcommand{{){re.escape(command.name)}(?![a-zA-Z])"
    result = re.sub(pattern, command.implementation, content)

    for i in range(command.num_params):
        pass
    
    return result
