# http://www.codeproject.com/KB/web-image/pnggammastrip.aspx

import struct
import sys
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import zlib


def read_signature(stream):
    return stream.read(8)


class Chunk:
    def __init__(self, size, chunk_type, data, crc):
        self.size = size
        self.chunk_type = chunk_type
        self.data = data
        self.crc = crc

    def __repr__(self):
        return repr(self.chunk_type) + " " + repr(self.size)

    def write(self, stream):
        stream.write(struct.pack("!I", self.size))
        stream.write(self.chunk_type)
        stream.write(self.data)
        stream.write(self.crc)

    @staticmethod
    def read(stream):
        len_string = stream.read(4)
        if not len_string:
            return None

        length = struct.unpack("!I", len_string)[0]
        chunk_type = stream.read(4)
        data = stream.read(length)
        crc = stream.read(4)
        return Chunk(length, chunk_type, data, crc)

    @staticmethod
    def create(chunk_type, data):
        data_length = len(data)
        payload = chunk_type + data
        chunk_crc = zlib.crc32(payload) & 0xFFFFFFFF
        return Chunk(data_length, chunk_type, data, struct.pack("!I", chunk_crc))


class iTXtChunk(Chunk):
    def __init__(self, chunk):
        Chunk.__init__(self, chunk.size, chunk.chunk_type, chunk.data, chunk.crc)
        keyword_length = self.data.find("\0")
        self.keyword = self.data[:keyword_length]
        self.text = str(self.data[keyword_length + 5 :], "utf-8")

    @staticmethod
    def create(keyword, text):
        """Create an uncompressed, untranslated iTXt chunk
        """
        null = "\0"
        uncompressed = "\0\0"

        chunk_data = keyword
        chunk_data += null
        chunk_data += uncompressed
        # no language specified
        chunk_data += null
        # no translated keyword
        chunk_data += null
        chunk_data += str(text).encode("utf-8")

        return Chunk.create("iTXt", chunk_data)


def all_chunks(stream):
    while True:
        chunk = Chunk.read(stream)

        if chunk:
            yield chunk
        else:
            return


if __name__ == "__main__":
    inputFilename = sys.argv[1]
    inputFile = file(inputFilename, "rb")
    read_signature(inputFile)

    for chunk in all_chunks(inputFile):
        print(chunk)
