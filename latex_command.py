import re

class LatexCommand:
    def __init__(self, command="newcommand", name="", implementation="", num_params=0, default_value = None):
        self.command = command
        self.name = name
        self.implementation = implementation
        self.num_params = num_params
        self.default_value = default_value


    def substitute_params(self, params):
        if self.num_params > len(params):
            params.insert(0, self.default_value)

        result = self.implementation
        for i in range(self.num_params):
            param_text = "#" + str(i + 1)
            result = result.replace(param_text, params[i])
        return result


    def get_tex_str(self):
        parts = [f"\\{self.command}{{{self.name}}}"]
        if self.num_params > 0:
            parts.append(f"[{self.num_params}]")
            if self.default_value != None:
                parts.append(f"[{self.default_value}]")
        parts.append(f"{{{self.implementation}}}")
        return "".join(parts)
