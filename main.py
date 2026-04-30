from path_processor import *

from latex_dd import *
from command_collector import *
from latex_command import LatexCommand


def process_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # commands = extract_commands(content)
    # result = content
    # for c in commands:
    #     print(f"\'{c.name}\': \'{c.implementation}\'")

    #     try:
    #         result = substitute_command(result, c)
    #     except Exception as e:
    #         pass
    #         #print(f"Exception in command {c.name}: {e}")

    # with open(output_path, 'w', encoding='utf-8') as file:
    #     file.write(result)


if __name__ == "__main__":
    input_file = "tests.tex"
    output_file = "tests_result.tex"
    process_file(input_file, output_file)

    # content = "\\newcommand{\\E}{exp} \\E{\\text{horse}}{2}\\E{2}{3} sometext\\Expeditor \\E{1}{2}34567890"
    # print(content)
    # c = LatexCommand("\E", 2, "TEST_{#1}^{#2}")
    # result = substitute_command(content, c)
