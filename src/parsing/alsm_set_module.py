from os import path
import re


def get_source_code_sample(filename):
    with open(filename) as f:
        source_code = f.read(40)  # just 12 chars
        source_code = re.sub(
            "\s+", " ", source_code
        ).strip()  # get rid of newlines and multiple spaces
        source_code += " ..."
    return source_code
