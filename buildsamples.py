"""
Takes all the files in the samples directory and converts them into a
dictionary resource, with the file contentes encoded in base64.
"""

import os, glob
from base64 import b64encode

samplesdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "src", "samples")
allfiles = glob.glob(os.path.join(samplesdir, "*.pyns"))

samples = {}
for file in allfiles:
    with open(os.path.join(samplesdir, file),'r') as f:
        samples[os.path.basename(file)] = b64encode(f.read())

OUTFILE = os.path.join(samplesdir, "files_as_resource.py")

with open(OUTFILE, 'w') as f:
    f.write("sample_files_dict = ")
    f.write(repr(samples))
    
print "done generating sample uml diagram file resource dictionary."
