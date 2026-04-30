import re

class LatexCommand:
    def __init__(self, name="", num_params=0, implementation=""):
        self.name = name
        self.implementation = implementation
        self.num_params = num_params


    def substitute_params(self, params):
        result = self.implementation
        for i in range(self.num_params):
            param_text = "#" + str(i + 1)
            result = result.replace(param_text, params[i])
            #result = re.sub(param_text, re.escape(params[i]), result)
        return result

    def get_tex_str(self):
        return f"\\newcommand{{{self.name}}}[{self.num_params}]{{{self.implementation}}}"
