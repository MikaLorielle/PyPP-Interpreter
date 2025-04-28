import re
import ast

class PyPPInterpreter:
    def __init__(self):
        self.indent_level = 0
        self.formatted_code = []
        self.block_stack = []
        self.block_type_stack = []
        self.raw_mode = False

    def add_line(self, stmt):
        if stmt.strip():
            self.formatted_code.append("    " * self.indent_level + stmt.strip())

    def handle_statement(self, token):
        token = token.strip()
        if not token:
            return

        if "=>" in token:
            parts = token.split("=>")
            params = parts[0].strip().strip('()')
            expr = parts[1].strip()
            token = f"lambda {params}: {expr}"

        if token.startswith("for ") and ":" in token and "in" not in token:
            match = re.match(r"for\s*\(\s*(\w+)\s*:\s*(.+?)\s*\)", token)
            if match:
                var, collection = match.groups()
                token = f"for {var} in {collection}"

        if token.startswith("switch("):
            expr = re.match(r"switch\((.*?)\)", token).group(1)
            self.add_line(f"match {expr}:")
            self.indent_level += 1
            return

        if token.startswith("case "):
            value = token[5:].strip()
            self.add_line(f"case {value}:")
            return

        if token.startswith("default"):
            self.add_line("case _:")
            return

        if token.startswith("return {") and token.endswith("}"):
            expr = token[7:-1].strip()
            token = f"return {expr}"

        self.add_line(token)

    def tokenize(self, code):
        lines = code.splitlines()
        self.indent_level = 0
        self.formatted_code = []
        self.block_stack = []
        self.raw_mode = False

        for line in lines:
            raw_line = line
            line = line.strip()
            if not line:
                continue

            if line.lstrip().startswith("PYL{"):
                self.raw_mode = True
                continue
            elif line.rstrip().endswith("}PYL"):
                self.raw_mode = False
                continue

            if self.raw_mode:
                self.formatted_code.append(raw_line)
                continue

            line = line.replace(r'\{', '{').replace(r'\}', '}')

            tokens = re.split(r'(\{|\}|;)', line)
            buffer = ""
            for token in tokens:
                token = token.strip()
                if not token:
                    continue

                if token == "{":
                    if buffer:
                        if buffer.startswith("switch("):
                            self.handle_statement(buffer)
                            self.block_type_stack.append("switch")
                        elif buffer.startswith("case ") or buffer.startswith("default"):
                            self.handle_statement(buffer)
                            self.block_type_stack.append("case")
                        else:
                            self.handle_statement(buffer + ":")
                            self.block_type_stack.append("normal")
                        buffer = ""
                    else:
                        if self.formatted_code:
                            self.formatted_code[-1] += ":"
                            self.block_type_stack.append("normal")
                    self.block_stack.append("{")
                    self.indent_level += 1

                elif token == "}":
                    if buffer:
                        self.handle_statement(buffer)
                        buffer = ""
                    if self.block_stack:
                        self.block_stack.pop()
                        block_type = self.block_type_stack.pop() if self.block_type_stack else "normal"
                        self.indent_level = max(0, self.indent_level - 1)

                elif token == ";":
                    if buffer:
                        self.handle_statement(buffer)
                        buffer = ""

                else:
                    if buffer:
                        buffer += " " + token
                    else:
                        buffer = token

            if buffer:
                self.handle_statement(buffer)

        return "\n".join(self.formatted_code)

    def parse_and_execute(self, code):
        try:
            tree = ast.parse(code)
            exec(compile(tree, filename="<string>", mode="exec"), globals())
        except Exception as e:
            print(f"Error: {e}")

    def run_file(self, file_path):
        if not file_path.endswith(".pypp"):
            print("Error: Only .pypp files are supported.")
            return

        try:
            with open(file_path, "r") as f:
                code = f.read()

            python_code = self.tokenize(code)
            #print(python_code)
            self.parse_and_execute(python_code)
        except FileNotFoundError:
            print("Error: File not found.")
