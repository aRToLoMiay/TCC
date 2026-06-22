import os

class TextFragment:
    def __init__(self, content: str = "", tex_file_path: str = "", active_rules = None, without_rules: bool = False):
        """
        Args:
            content: Хранимый текст (строка).
            tex_file_path: Путь к связанному файлу.
            active_rules: Список активных правил (целочисленные идентификаторы).
            without_rules: Флаг, принудительно игнорирующи список правил.
        """
        self.content = content
        self.tex_file_path = tex_file_path
        self.active_rules = active_rules if active_rules is not None else []
        self.without_rules = without_rules


    def add_rule(self, rule_id: int) -> None:
        if rule_id not in self._active_rules:
            self.active_rules.append(rule_id)


    def remove_rule(self, rule_id: int) -> bool:
        if rule_id in self._active_rules:
            self.active_rules.remove(rule_id)
            return True
        return False


    def has_rule(self, rule_id: int) -> bool:
        return rule_id in self.active_rules


    def clear_rules(self) -> None:
        self.active_rules.clear()


    def create_copy(self) -> None:
        copy = TextFragment(self.content, self.tex_file_path, self.active_rules, self.without_rules)
        return copy


    def separate_tail(self, pos: int):
        copy = self.create_copy()
        self.content = self.content[:pos]
        copy.content = copy.content[pos:]
        return copy


    def append(self, fragment):
        self.content += fragment.content


    def is_blank(self) -> bool:
        if self.content == "":
            return True
        return self.content.isspace()


# --------------------------------------------------------------------------------
# Additional functions.
# --------------------------------------------------------------------------------
def collect_fragments_content(fragments, skip_without_rules=False):
    return "".join(f.content for f in fragments if not skip_without_rules or not f.without_rules)
