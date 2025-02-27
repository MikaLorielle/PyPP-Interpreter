import re
import ast

class PyPPInterpreter:
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

            line = re.sub(r'\\{', '{', line)
            line = re.sub(r'\\}', '}', line)

            if re.search(r"=\s*\{.*?\}|\breturn\b\s*\{.*?\}|\[.*?\{.*?\}.*?\]", line):
                formatted_code.append("    " * indent_level + line)
                continue

            match = re.match(r"(\w+)\s*=\s*lambda\s*\((.*?)\)\s*\{(.*?)\}", line)
            if match:
                func_name, params, body = match.groups()
                formatted_code.append(
                    "    " * indent_level + f"{func_name} = lambda {params}: {body.strip()}"
                )
                continue

            match = re.match(r"switch\s*\((.*?)\)\s*\{(.*?)\}", line, re.DOTALL)
            if match:
                switch_var, body = match.groups()
                formatted_code.append("    " * indent_level + f"match {switch_var}:")
                indent_level += 1

                cases = re.findall(r"case\s+(.*?)\s*\{(.*?)\}", body, re.DOTALL)
                for case_value, case_body in cases:
                    formatted_code.append("    " * indent_level + f"case {case_value}:")
                    indent_level += 1
                    for stmt in case_body.split(";"):
                        stmt = stmt.strip()
                        if stmt:
                            formatted_code.append("    " * indent_level + stmt)
                    indent_level -= 1

                default_match = re.search(r"default\s*\{(.*?)\}", body, re.DOTALL)
                if default_match:
                    default_body = default_match.group(1)
                    formatted_code.append("    " * indent_level + "case _:")
                    indent_level += 1
                    for stmt in default_body.split(";"):
                        stmt = stmt.strip()
                        if stmt:
                            formatted_code.append("    " * indent_level + stmt)
                    indent_level -= 1

                indent_level -= 1
                continue

            match = re.match(r"(def\s+\w+\s*\(.*?\))\s*\{(.*)\}", line)
            if match:
                function_def, body = match.groups()
                formatted_code.append("    " * indent_level + function_def + ":")
                indent_level += 1
                for stmt in body.split(';'):
                    stmt = stmt.strip()
                    if stmt:
                        formatted_code.append("    " * indent_level + stmt)
                indent_level -= 1
                continue

            match = re.match(r"(class\s+\w+)\s*\{(.*)\}", line)
            if match:
                class_def, body = match.groups()
                formatted_code.append("    " * indent_level + class_def + ":")
                indent_level += 1
                body = body.strip().rstrip(";")
                methods = re.findall(r"(def\s+\w+\s*\(.*?\))\s*\{(.*?)\}", body)
                for method_def, method_body in methods:
                    formatted_code.append("    " * indent_level + method_def + ":")
                    for stmt in method_body.split(";"):
                        stmt = stmt.strip()
                        if stmt:
                            formatted_code.append("    " * (indent_level + 1) + stmt)
                indent_level -= 1
                continue

            match = re.match(r"(if|elif|else)\s*(\(?.*?\)?)\s*\{(.*)\}", line)
            if match:
                keyword, condition, body = match.groups()
                formatted_code.append("    " * indent_level + f"{keyword} {condition}:")
                indent_level += 1
                for stmt in body.split(';'):
                    stmt = stmt.strip()
                    if stmt:
                        formatted_code.append("    " * indent_level + stmt)
                indent_level -= 1
                continue

            match = re.match(r"(while|for)\s*(\(?.*?\)?)\s*\{(.*)\}", line)
            if match:
                keyword, condition, body = match.groups()
                formatted_code.append("    " * indent_level + f"{keyword} {condition}:")
                indent_level += 1
                for stmt in body.split(';'):
                    stmt = stmt.strip()
                    if stmt:
                        formatted_code.append("    " * indent_level + stmt)
                indent_level -= 1
                continue

            if re.search(r'f".*?\{.*?\}.*?"', line) or re.search(r"f'.*?\{.*?\}.*?'", line):
                formatted_code.append("    " * indent_level + line)
                continue

            if "{" in line and not re.search(r"=\s*\{|:\s*\{", line) and not re.search(r'f".*?\{.*?\}.*?"', line):
                line = line.replace("{", ":")
                formatted_code.append("    " * indent_level + line)
                block_stack.append("{")
                indent_level += 1
                continue

            if "}" in line:
                if block_stack:
                    block_stack.pop()
                indent_level = max(0, indent_level - 1)
                line = line.replace("}", "").strip()
                if line:
                    statements = line.split(';')
                    for stmt in statements:
                        stmt = stmt.strip()
                        if stmt:
                            formatted_code.append("    " * indent_level + stmt)
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
        if not file_path.endswith(".pypp"):
            print("Error: Only .pypp files are supported.")
            return

        try:
            with open(file_path, "r") as f:
                code = f.read()

            python_code = self.tokenize(code)
            #print("Transpiled Python code:")
            #print(python_code)
            self.parse_and_execute(python_code)
        except FileNotFoundError:
            print("Error: File not found.")
