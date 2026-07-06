from TCC_processor import TccProcessor

from console_menu import create_file_menu
from path_processor import (
    collect_file_paths,
    get_app_path,
)

import os


def start_console_TCC():
    # Create function for text extraction from menu.
    menu = create_file_menu(
        menu_title="Select tex-file for processing:",
        path=get_app_path(),
        file_types=('.tex'),
        recursive=True)
    menu.run()

    # Get files list.
    tex_files = collect_files('.tex')
    sty_files = collect_files('.sty')

    # Start processing.
    processor = TccProcessor(tex_files_list=tex_files, 
                             sty_files_list=sty_files)
    result = processor.process_tex(menu.result)

    # Result saving.
    for key in result.keys():
        print(f"=== Start of fragment : {key} ===")
        print(result[key])
        print(f"===   End of fragment : {key} ===")


def collect_files(file_type):
    file_types = (file_type)
    work_dir = get_app_path()
    paths = collect_file_paths(work_dir, file_types, True)
    paths = [os.path.relpath(path, work_dir) for path in paths]
    return paths
