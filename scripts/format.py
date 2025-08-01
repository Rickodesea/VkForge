import sys
import argparse
import re


def make_c_format_string(
    c_code: str, use_source_formatter: bool = False
) -> tuple[str, dict]:
    """
    Escapes {, }, and % for safe use with .format().
    If use_source_formatter is True, replaces FORMAT(name, value) with {name}.
    Also returns a dict of name-value pairs found.
    """
    substitutions = {}

    if use_source_formatter:
        # Find all FORMAT(name, value) patterns
        pattern = re.compile(r"FORMAT\s*\(\s*(\w+)\s*,\s*(.*?)\s*\)")

        def replacer(match):
            name = match.group(1)
            value = match.group(2)
            substitutions[name] = value
            return f"{{{name}}}"

        c_code = pattern.sub(replacer, c_code)

    # Escape the remaining special characters
    escaped = c_code.replace("%", "%%").replace("{", "{{").replace("}", "}}")

    # If we used FORMAT(name, value), re-insert the unescaped {name}
    if use_source_formatter:
        # Replace the escaped {{name}} with {name}
        for name in substitutions.keys():
            escaped = escaped.replace(f"{{{{{name}}}}}", f"{{{name}}}")

    return escaped, substitutions


def generate_python_function(
    func_name: str, fmt_string: str, params: str = "", substitutions: dict = None
) -> str:
    """
    Generates a Python function definition with the given name, params, and content.
    If substitutions are given, includes them in the .format() call.
    """
    param_part = params.strip()
    if param_part:
        param_str = param_part
    else:
        param_str = ""

    # Prepare the .format(...) call
    if substitutions:
        subs_str = ", ".join([f"{k}={v}" for k, v in substitutions.items()])
        format_call = f"output = content.format({subs_str})"
    else:
        format_call = "output = content.format()"

    return f'''def {func_name}({param_str}) -> str:
    content = """\\
{fmt_string}

"""
    {format_call}

    return output
'''


def main():
    parser = argparse.ArgumentParser(description="Format a file for use in Python.")
    parser.add_argument("input_file", help="Path to the input file")
    parser.add_argument(
        "--pydef",
        metavar="FUNC_NAME",
        help="Generate a Python function with the given name",
    )
    parser.add_argument(
        "--pydef-params",
        metavar="PARAMS",
        help="Parameter list for the generated function",
    )
    parser.add_argument(
        "--use-source-formatter",
        action="store_true",
        help="Enable FORMAT(name, value) replacement",
    )

    args = parser.parse_args()

    try:
        with open(args.input_file, "r", encoding="utf-8") as f:
            raw_c_code = f.read()
    except FileNotFoundError:
        print(f"File not found: {args.input_file}")
        sys.exit(1)

    fmt_string, substitutions = make_c_format_string(
        raw_c_code, use_source_formatter=args.use_source_formatter
    )

    if args.pydef:
        params = args.pydef_params if args.pydef_params else ""
        result = generate_python_function(args.pydef, fmt_string, params, substitutions)
        print(result)
    else:
        print("---- Formattable C Code ----")
        print(fmt_string)


if __name__ == "__main__":
    main()
