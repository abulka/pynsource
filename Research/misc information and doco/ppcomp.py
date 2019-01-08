# ppcomp.py
# pretty print some compiler output -- bokr@oz.net 2002-12-17
import compiler, re, sys

rxb = re.compile(r"([\[\](),])")
IND = "  "


def ppcomp(s):
    out = []
    wrout = out.append  # sys.stdout.write
    sp = [s.strip() for s in rxb.split(repr(compiler.transformer.parse(s)))]
    nest = 0
    for t in sp:
        if not t:
            continue
        if t in ["(", "["]:
            wrout(t)
            nest += 1
            wrout("\n")
            wrout(IND * nest)
        elif t in [")", "]"]:
            wrout(t)
            nest -= 1
        else:
            wrout(t)
            if t == ",":
                wrout("\n")
                wrout(IND * nest)
    # make vertical connecting lines
    out = "".join(out).splitlines()
    nl = len(out)
    linewd = []
    for y in range(nl):
        linewd.append(len(out[y]) - len(out[y].lstrip()))
    lastwd = 0
    for y in range(nl):
        w = linewd[y]
        if w >= lastwd:
            lastwd = w
            continue
        # draw line upwards if spaces above when indent decreases
        ydraw = y - 1
        while ydraw >= 0 and w < linewd[ydraw] and out[ydraw][w] == " ":
            s = out[ydraw]
            out[ydraw] = s[:w] + "|" + s[w + 1 :]
            ydraw -= 1
    return "\n".join(out)


if __name__ == "__main__":
    import sys

    s = ""
    if len(sys.argv) < 2:
        print("Enter Python source and end with ^Z")
        s = sys.stdin.read()
    elif sys.argv[1] == "-f" and len(sys.argv) > 2:
        f = file(sys.argv[2])
        s = f.read()
        f.close()
    elif sys.argv[1] == "-i":
        s = "anything"
        print("Enter expression (or just press Enter to quit):")
        while s:
            s = input("Expr> ").rstrip()
            if s:
                print(ppcomp(s))
    elif sys.argv[1] == "-h":
        print(
            """
Usage:  python ppcomp.py [-i | -h | -f filename | expression ]
        (nothing specified reads stdin, -i prompts, -h prints this, else the obvious)
"""
        )
    else:
        s = sys.argv[1]
    if s:
        print(ppcomp(s))
