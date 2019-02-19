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

    with open(OUTFILE, "w") as f:
        f.write("from collections import OrderedDict\n")  # allow file to be valid python
        f.write("sample_files_dict = ")
        f.write(repr(od))

print("done generating sample uml diagram file resource dictionary.")
