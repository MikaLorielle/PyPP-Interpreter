import re
import ast


class BryInterpreter:
    def __init__(self):
        pass

    def tokenize(self, code):
        lines = code.splitlines()
        indent_level = 0
        formatted_code = []
        block_stack = []

        for line in lines:
            line = line.strip()

            if not line:
                continue

            match = re.match(r"(def\s+\w+\s*\(.*?\))\s*\{(.*)\}", line)
            if match:
                function_def, body = match.groups()
                formatted_code.append("    " * indent_level + function_def + ":")
                for stmt in body.split(';'):
                    stmt = stmt.strip()
                    if stmt:
                        formatted_code.append("    " * (indent_level + 1) + stmt)
                continue

            match = re.match(r"(class\s+\w+)\s*\{(.*)\}", line)
            if match:
                class_def, body = match.groups()
                formatted_code.append("    " * indent_level + class_def + ":")
                body = body.strip().rstrip(";")

                methods = re.findall(r"(def\s+\w+\s*\(.*?\))\s*\{(.*?)\}", body)
                for method_def, method_body in methods:
                    formatted_code.append("    " * (indent_level + 1) + method_def + ":")
                    for stmt in method_body.split(";"):
                        stmt = stmt.strip()
                        if stmt:
                            formatted_code.append("    " * (indent_level + 2) + stmt)

                remaining_body = re.sub(r"(def\s+\w+\s*\(.*?\))\s*\{.*?\}", "", body).strip()
                if remaining_body:
                    for stmt in remaining_body.split(";"):
                        stmt = stmt.strip()
                        if stmt:
                            formatted_code.append("    " * (indent_level + 1) + stmt)
                continue

            match = re.match(r"(if|elif|else)\s*(\(?.*?\)?)\s*\{(.*)\}", line)
            if match:
                keyword, condition, body = match.groups()
                formatted_code.append("    " * indent_level + f"{keyword} {condition}:")
                for stmt in body.split(';'):
                    stmt = stmt.strip()
                    if stmt:
                        formatted_code.append("    " * (indent_level + 1) + stmt)
                continue

            match = re.match(r"(while|for)\s*(\(?.*?\)?)\s*\{(.*)\}", line)
            if match:
                keyword, condition, body = match.groups()
                formatted_code.append("    " * indent_level + f"{keyword} {condition}:")
                for stmt in body.split(';'):
                    stmt = stmt.strip()
                    if stmt:
                        formatted_code.append("    " * (indent_level + 1) + stmt)
                continue

            if "{" in line:
                line = line.replace("{", ":")
                formatted_code.append("    " * indent_level + line)
                block_stack.append("{")
                indent_level += 1
                continue

            if "}" in line:
                if block_stack:
                    block_stack.pop()
                indent_level = max(0, indent_level - 1)
                continue

            statements = line.split(';')
            for stmt in statements:
                stmt = stmt.strip()
                if stmt:
                    formatted_code.append("    " * indent_level + stmt)

        return "\n".join(formatted_code)

    def parse_and_execute(self, code):
        try:
            tree = ast.parse(code)
            exec(compile(tree, filename="<string>", mode="exec"), globals())
        except Exception as e:
            print(f"Error: {e}")

    def run_file(self, file_path):
        if not file_path.endswith(".bry"):
            print("Error: Only .bry files are supported.")
            return

        try:
            with open(file_path, "r") as f:
                code = f.read()

            python_code = self.tokenize(code)
            #print("Transpiled Python Code:\n" + python_code + "\n") # converted code
            self.parse_and_execute(python_code)

        except FileNotFoundError:
            print("Error: File not found.")
