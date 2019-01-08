def add_line_numbers(s):
    result = ""
    for (number, line) in enumerate(s.split("\n")):
        result += "%3d  %s\n" % (number + 1, line)
    return result
