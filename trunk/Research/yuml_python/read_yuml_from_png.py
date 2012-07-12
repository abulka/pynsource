import png

def read(pngFilename):
    yuml = '<<no yuml found>>'
    pngFile = file(pngFilename, 'rb')
    png.read_signature(pngFile)
    for chunk in png.all_chunks(pngFile):
        if chunk.chunk_type == 'iTXt':
            chunk = png.iTXtChunk(chunk)
            if chunk.keyword == 'yuml':
                yuml = chunk.text
                break
    pngFile.close()
    return yuml

if __name__ == '__main__':
    import sys
    sys.exit(read(sys.argv[1]))
