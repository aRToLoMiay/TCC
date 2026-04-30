import re

from path_processor import *


def collect_tex():
    types = ('.tex', '.sty')
    files = collect_file_paths(get_app_path(), types)

    content = ""
    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
            file_content = clear_comments(file_content)
            file_content = content_gluing(file_content)
            content = content.join(file_content)
    return content


def clear_comments(content):
    return re.sub(r'%.*$', '', content, flags=re.MULTILINE)


def content_gluing(content):
    result = re.sub(r'(?m)^[ \t]+', '', content)
    result = re.sub(r'[\n\r]+', '', result)
    return result
