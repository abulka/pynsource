"""
Takes all the files in the samples directory and converts them into a
dictionary resource, with the file contentes encoded in base64.
"""

import os, glob
from base64 import b64encode
import collections

ORDERED = True

samplesdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "src", "samples")
allfiles = glob.glob(os.path.join(samplesdir, "*.pyns"))

samples = {}
for file in allfiles:
    with open(os.path.join(samplesdir, file), "r") as f:
        samples[os.path.basename(file)] = b64encode(f.read().encode("utf-8"))

OUTFILE = os.path.join(samplesdir, "files_as_resource.py")

if not ORDERED:
    with open(OUTFILE, "w") as f:
        f.write("sample_files_dict = ")
        f.write(repr(samples))
else:
    # od = collections.OrderedDict(samples.items())
    od = collections.OrderedDict()
    for key in sorted(samples.keys()):
        od[key] = samples[key]

    # Write a plain dict, not an OrderedDict: dicts are insertion-ordered (3.7+) and, unlike
    # OrderedDict, their repr has been stable across Python versions. OrderedDict's repr
    # changed in CPython 3.12 ("OrderedDict([('k', v)])" -> "OrderedDict({'k': v})"), which
    # made this generated file churn every time someone built with a different interpreter.
    with open(OUTFILE, "w") as f:
        f.write("sample_files_dict = ")
        f.write(repr(dict(od)))
        f.write("\n")

print("done generating sample uml diagram file resource dictionary.")
