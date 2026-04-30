from path_processor import *

from latex_dd import *
from command_collector import *
from latex_command import LatexCommand


if __name__ == "__main__":
    # files = collect_file_paths(get_app_path(), ('.tex'))

    # commands = extract_commands(files[0])

    # for command in commands:
    #     print(f"{command.name}[{command.num_params}]{{{command.implementation}}}")
    # content = collect_tex()
    # extract_commands(content)

    content = "\\newcommand{\\E}{exp} sometext\\Expeditor \\E123"
    c = LatexCommand("\E", 0, "exp")
    print(substitute_command(content, c))
