"""
  prtok.py

  Find all identifiers in a python proram.

e.g.

C:\Documents and Settings\Administrator\Desktop>prtok.py prtok.py

====< prtok.py >====
  (Multicase symbols)
         tokstr:6            TOKSTR:4
           NAME:1              name:2
  (Singlecase symbols)
         append:1              argv:1             clear:1               def:1
            end:1            import:1              keys:1               len:1
           line:1              open:1                or:1          readline:1
           sort:1             start:1             upper:1              else:2
       fileglob:2           has_key:2             items:2         multicase:2
              n:2               sys:2             token:2        tokeneater:2
           type:2              None:3          filename:3              glob:3
            npr:3        singlecase:3          tokenize:3                 d:4
           freq:4                 k:4            byfreq:5               for:8
             if:8                in:8               key:8            header:10
          print:10           symdir:11

C:\Documents and Settings\Administrator\Desktop>
"""


import sys, tokenize, glob, token

symdir = {}


def tokeneater(type, tokstr, start, end, line, symdir=symdir):
    if type == token.NAME:
        TOKSTR = tokstr.upper()  # should show up for this file
        if TOKSTR in symdir:
            d = symdir[TOKSTR]
            if tokstr in d:
                d[tokstr] += 1
            else:
                d[tokstr] = 1
        else:
            symdir[TOKSTR] = {tokstr: 1}


for fileglob in sys.argv[1:]:
    for filename in glob.glob(fileglob):
        symdir.clear()
        tokenize.tokenize(open(filename).readline, tokeneater)

        header = "\n====< " + filename + " >===="
        singlecase = []
        multicase = [
            key for key in list(symdir.keys()) if len(symdir[key]) > 1 or singlecase.append(key)
        ]
        for key in multicase:
            if header:
                print(header)
                print("  (Multicase symbols)")
                header = None
            for name, freq in list(symdir[key].items()):
                print("%15s:%-3s" % (name, freq), end=" ")
            print()
        if header:
            print(header)
            header = None
        print("  (Singlecase symbols)")
        byfreq = [list(symdir[k].items())[0] for k in singlecase]
        byfreq = [(n, k) for k, n in byfreq]
        byfreq.sort()
        npr = 0
        for freq, key in byfreq:
            if header:
                print(header)
                header = None
            print("%15s:%-3s" % (key, freq), end=" ")
            if npr % 4 == 3:
                print()
            npr += 1
        print()

"""
========================================================================
Operating on itself and another little file (you can specify file glob expressions too):

[18:55] C:\pywk\tok>prtok.py prtok.py gt.py

====< prtok.py >====
  (Multicase symbols)
         tokstr:6            TOKSTR:4
           NAME:1              name:2
  (Singlecase symbols)
         append:1              argv:1             clear:1
            def:1               end:1            import:1              keys:1
            len:1              line:1              open:1                or:1
       readline:1              sort:1             start:1             upper:1
           else:2          fileglob:2           has_key:2             items:2
      multicase:2                 n:2               sys:2             token:2
     tokeneater:2              type:2              None:3          filename:3
           glob:3               npr:3        singlecase:3          tokenize:3
              d:4              freq:4                 k:4            byfreq:5
            for:8                if:8                in:8               key:8
         header:10            print:10           symdir:11

====< gt.py >====
  (Singlecase symbols)
       __name__:1              argv:1               def:1
             if:1                fn:2               for:2            import:2
             in:2              main:2             print:2               sys:2
            arg:3              glob:3

Regards,
Bengt Richter
"""
