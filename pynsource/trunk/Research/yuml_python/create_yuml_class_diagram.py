
import urllib
import urllib2

import png

def add_yuml_to_png(yuml, in_stream, out_stream):
    signature = png.read_signature(in_stream)
    out_stream.write(signature)
    
    for chunk in png.all_chunks(in_stream):
        if chunk.chunk_type == 'IEND':
            break
        chunk.write(out_stream)

    itxt_chunk = png.iTXtChunk.create('yuml', yuml)
    itxt_chunk.write(out_stream)

    # write the IEND chunk
    chunk.write(out_stream)
    

def create(yuml, output_filename):
    baseUrl = 'http://yuml.me/diagram/scruffy/class/'
    url = baseUrl + urllib.quote(yuml)
    
    original_png = urllib2.urlopen(url)
    output_file = file(output_filename, 'wb')

    add_yuml_to_png(yuml, original_png, output_file)

    output_file.close()
        
if __name__ == '__main__':
    import sys
    sys.exit(create(*sys.argv[1:3]))
