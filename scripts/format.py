import sys

def make_c_format_string(c_code: str) -> str:
    """
    Escapes {, }, and % for safe use with .format().
    """
    escaped = (
        c_code
        .replace('%', '%%')
        .replace('{', '{{')
        .replace('}', '}}')
    )
    return escaped

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        with open(input_file, "r", encoding="utf-8") as f:
            raw_c_code = f.read()

        fmt_string = make_c_format_string(raw_c_code)

        print("---- Formattable C Code ----")
        print(fmt_string)
    else:
        print("format.py [input-file]")
