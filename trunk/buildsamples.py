import os, glob

samplesdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "src", "samples")
#allfiles = os.listdir(samplesdir)
allfiles = glob.glob(os.path.join(samplesdir, "*.pyns"))

#import StringIO 
#import uu 

from base64 import b64encode

#with open(os.path.join(samplesdir, allfiles[0]),'r') as f:
#    s = f.read()
#print b64encode(s)
#exit(0)
#
#import operator 
#infile = open(os.path.join(samplesdir, allfiles[0]),'r') 
#outfile = StringIO.StringIO()
#uu.encode(infile, outfile)
#print outfile.buflist 
#
#exit(0)
#
#def uu2string(data, mode=None): 
#    outfile = StringIO.StringIO() 
#    infile = StringIO.StringIO(data) 
#    uu.decode(infile, outfile, mode) 
#    return outfile.getvalue()
#
#print uu2string("ABCDEF")
#exit(0)

#glob.glob(pathname)


samples = {}
for file in allfiles:
    with open(os.path.join(samplesdir, file),'r') as f:
        samples[os.path.basename(file)] = b64encode(f.read())

#print samples.keys()
import pprint
#pprint.pprint(samples)

#OUTFILE = "out.py"
OUTFILE = os.path.join(samplesdir, "files_as_resource.py")

with open(OUTFILE, 'w') as f:
    f.write("sample_files_dict = ")
    #pprint.pprint(str(samples), f, indent=4)
    f.write(repr(samples))
print "done"
