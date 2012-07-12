import struct, time

def readString(fp):
    fmt = int8
    block = fp.read(struct.calcsize(fmt))
    numchars = struct.unpack(fmt, block)[0]   # get pos 0 cos a tuple always returned e.g. (12,)

    fmt = "s"
    str = fp.read(numchars)
    return str

def read32(fp):
    fmt = '>'+int32
    block = fp.read(struct.calcsize(fmt))
    return struct.unpack(fmt, block)[0]

def read16(fp):
    fmt = '>'+int16
    block = fp.read(struct.calcsize(fmt))
    return struct.unpack(fmt, block)[0]

def read8(fp):
    # result (int8)
    fmt = int8
    block = fp.read(struct.calcsize(fmt))
    return struct.unpack(fmt, block)[0]

def YesOrNo(bool):
    if bool:
        return 'Yes'
    else:
        return 'No'

class Flags:
    def __init__(self, fp):
        self.flags = []
        self.readFlags(fp)

    def readFlags(self, fp):
        """
        flag[NrFlags]	flags

        flag
        ----
        int16	x location (meters)
        int16	y location (meters)
        uint8	owner (0: neutral, 1:axis, 2:allied)
        """
        self.numberOfFlags = read16(fp)
        for flagcount in range(0, self.numberOfFlags):
            flag = Flag(fp)
            self.AddFlag(flag)

    def AddFlag(self, flag):
        self.flags.append(flag)

    def __repr__(self):
        msg = ""
        assert self.numberOfFlags == len(self.flags)
        if not self.numberOfFlags:
            msg += "NO FLAGS\n"
        else:
            msg += "FLAGS: (%d) of them ------ \n" % len(self.flags)
            for flag in self.flags:
                msg += "\t%s\n" % flag
        return msg

class Flag:
    def __init__(self, fp):
        self.readflag(fp)

    def readflag(self, fp):
        self.flagx = read16(fp)
        self.flagy = read16(fp)
        self.owner = read8(fp)
    
    def __repr__(self):
        msg = ""
        msg += "flag at %d, %d owned by %s" % ( self.flagx, self.flagy, lookup_flagowner[self.owner] )
        return msg
