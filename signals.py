"""
Signals   05/30/2025

    Signal,
        AdBreakSignal
        SpliceSignal
        ABTSignal
        RestrictDescriptor

 note on vars:
        *   A number that will be used in any kind of math, will be an integer or float.
        *   If a  number is used as identification it is displayed in hex with the leading '0x'.
        *   Time values are stored as ticks and displayed as float rounded to 6 decimal places.

"""

from collections import deque

NTK = 90000


class Signal:
    """
    Signal is the base class for AdBreakSignal, SpliceSignal and ABTSignal.
    """

    def __init__(self, data=None):
        self.startmark = "qq"
        self.data = data
        self.qq_type = None  # 1 byte
        self.qqid = None  # 2 bytes
        self.data_length = None  # 2 bytes

    def __repr__(self):
        return str(vars(self))

    def decode_head(self):
        """
        decode bytes into Signal vars.
        """
        self.startmark = self.data[0:2]
        self.qq_type = self.data[2:3]
        self.qqid = self.hex(self.data[3:5])
        self.data_length = self.int(self.data[5:7])

    def decode(self):
        self.decode_head()

    def encode_head(self):
        """
        encode bytes into  Signal vars.
        """
        qq = b"qq"
        qq += self.qq_type
        qq += self.hex2bytes(self.qqid, 2)
        qq += self.int2bytes(self.data_length, 2)
        return  qq

    def encode(self):
        return self.encode_head()

    def hex(self, bites):
        """
        hex return bites as a hex value prefixed by 0x
        """
        return hex(self.int(bites))

    @staticmethod
    def int(bites):
        """
        int return bites as an integer
        """
        return int.from_bytes(bites, byteorder="big")

    def seconds(self, bites):
        """
        seconds return bites as seconds from a 90k clock
        """
        return self.int(bites) / NTK

    @staticmethod
    def int2bytes(integer, howmany):
        """
        int2bytes convert int to bytes for encoding
        """
        return int(integer).to_bytes(length=howmany, byteorder="big")

    @staticmethod
    def hex2bytes(hexed, howmany):
        """
        hex2bytes convert hex to bytes for encoding
        """
        return int(hexed, base=16).to_bytes(length=howmany, byteorder="big")

    @staticmethod
    def seconds2bytes(seconds, howmany):
        """
        seconds2bites convert seconds to bytes for encoding
        """
        return int(seconds * NTK).to_bytes(length=howmany, byteorder="big")


class AdBreakSignal(Signal):
    """
    AdBreakSinal class
    """

    def __init__(self, data=None):
        super().__init__(data)
        self.qq_type = b"ab"
        self.break_starts_in = 0  # ticks until adbreak start
        self.splice_points = []  # splice signals included in adbreak
        self.data = data

    def decode(self):
        super().decode(self.data)
        self.break_starts_in = self.seconds(self.data[7:11])
        data = self.data[11:]
        while data:
            splice_point, data = qqheader()
            splice_point.decode()
            self.splicepoints.append(splice_point)

    def encode(self):
        qq = self.seconds2bytes(self.break_starts_in, 4)
        self.data_length= len(qq)
        qqbase = super().encode()
        self.data = qqbase + qq
        return self.data


class ABTSignal(Signal):
    """
    ABTSignal AdBreak Terminate Signal
    Used to return early from an Ad Break.

    @ break_stops_in  a 32 bit value on a 90k clock,
        ticks until an ad break is terminated.
        a value of 0 indicates immediate terminate.
    """

    def __init__(self, data=None):
        super().__init__(data)
        self.qq_type = b"\xae"
        self.break_stops_in = 0
        self.data = b""

    def decode(self):
        """
        decode bytes into ABTSignal vars.
        """
        super().decode(self.data)
        self.break_stops_in = self.seconds(self.data[7:11])

    def encode(self):
        """
        encode  ABTSignal vars into bytes
        """
        qq = self.seconds2bytes(self.break_stops_in, 4)
        self.data_length= len(qq)
        qqbase = super().encode()
        self.data = qqbase + qq
        return self.data


class SpliceSignal(Signal):
    """
    SpliceSignal Class
    """

    def __init__(self, data=None):
        super().__init__(data)
        self.qq_type = b"\xac"
        self.sap_type = None
        self.tier = None
        self.break_duration = 0
        self.descriptors = []
        self.data = data

    def decode(self):
        """
        decode bytes into SpliceSignal vars.
        """
        super().decode()
        self.sap_type = hex(self.data[7])
        self.tier = self.hex(self.data[8:10])
        self.break_duration = self.seconds(self.data[10:14])
        # pass anything left to unroll_descriptors()
        self.unroll_descriptors(self.data[14:])

    def unroll_descriptors(self, data):
        """
        unroll_descriptors decode descriptors from bites
        """
        while data:
            descriptor, data = qqheader(data)
            descriptor.decode()
            self.descriptors.append(descriptor)

    def roll_descriptors(self):
        """
        roll_descriptors turns descriptors into bytes for encoding
        """

        return b"".join([descriptor.encode() for descriptor in self.descriptors])

    def encode(self):
        """
        encode SpliceSignal vars into bytes.
        """
        qq = self.hex2bytes(self.sap_type, 1)
        qq += self.hex2bytes(self.tier, 2)
        qq += self.seconds2bytes(self.break_duration, 4)
        qq += self.roll_descriptors()
        self.data_length= len(qq)
        qqbase = super().encode()
        self.data = qqbase  + qq
        return self.data

class RestrictDescriptor(Signal):

    def __init__(self,data=None):
        super().__init__(data)
        self.data = data
        self.qq_type=b'\xad'
        self.web_delivery_allowed_flag=None  # 1 bit
        self.no_regional_blackout_flag= None # 1 bit
        self.archive_allowed_flag= None# 1 bit
        self.device_restrictions = None    # 2 bits

    def decode(self):
        magic_byte =self.data[7] # top 3 bits are 0
        self.web_delivery_allowed_flag= bool((magic_byte & 16) >>4)
        self.no_regional_blackout_flag= bool( (magic_byte & 8) >> 3)
        self.archive_allowed_flag= bool((magic_byte & 4 )>> 2)
        self.device_restrictions= hex(magic_byte & 3)

    def encode(self):
        magic_byte=0
        magic_byte +=int(self.web_delivery_allowed_flag) << 4  & 16
        magic_byte +=int(self.no_regional_blackout_flag) << 3  & 8
        magic_byte +=int(self.archive_allowed_flag) << 2 & 4
        magic_byte +=int(self.device_restrictions,base=16) & 3
        self.data_length=1
        qq= super().encode()
        self.data=qq+bytes([magic_byte])
        return self.data





qq_map = {
    b"\xab": AdBreakSignal,
    b"\xac": SpliceSignal,
    b"\xad": RestrictDescriptor,
    b"\xae": ABTSignal,
}


def qqheader(data):
    """
    qqheader finds the first qq object in data,
    initializes it based on the header, and then returns
    a tuple of the object and  the remaining data
    """
    startmark = b"qq"
    head_size = 7
    start = data.find(startmark)
    qq_type = data[start + 2:start+3]
    qqid = hex(int.from_bytes(data[start + 3 : start + 5], byteorder="big"))
    data_length = int.from_bytes(data[start + 5 : start + 7], byteorder="big")
    end = data_length + head_size
    obj_data = data[start:end]
    obj = qq_map[qq_type](obj_data)
    leftover = data[end:]
    return obj, leftover
