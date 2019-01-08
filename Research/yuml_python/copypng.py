# http://www.codeproject.com/KB/web-image/pnggammastrip.aspx

import sys
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse

import pnglib

inputFilename = sys.argv[1]
outputFilename = sys.argv[2]

data = file(inputFilename, "rb")

outputFile = file(outputFilename, "wb")
signature = pnglib.read_signature(data)
outputFile.write(signature)

for chunk in png.all_chunks(data):
    chunk.write(outputFile)


outputFile.close()
