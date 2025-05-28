"""
Signals   05/28/2025

    Signal,
        AdBreakSignal
        SpliceSignal
        ABTSignal

"""

from collections import deque

NTK = 90000

qq_map = {
    b"a": AdBreakSignal,
    b"s": SpliceSignal,
    b"t": ABTSignal,
    b"r": RestrictDescriptor,
    b"d": SegmentDescriptor,
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
    signal_type = data[start + 2]
    qid = data[start + 3 : start + 5]
    data_length = data[start + 5 : start + 7]
    end = data_length + head_size
    obj_data = data[start:end]
    obj = qq_map[signal_type](obj_data)
    leftover = data[end:]
    return obj, leftover


class Signal:
    """
    Signal is the base class for AdBreakSignal, SpliceSignal and ABTSignal.
    """

    def __init__(self, data=None):
        self.startmark = "qq"
        self.data = data
        self.signal_type = None  # 1 byte
        self.qid = None  # 2 bytes
        self.data_length = None  # 2 bytes

    def decode_head(self):
        """
        decode bytes into Signal vars.
        """
        self.startmark = self.data[0:2]
        self.signal_type = self.data[2]
        self.qid = self.hex(self.data[3:5])
        self.data_length = self.int(self.data[5:7])

    def decode(self):
        self.decode_head()

    def encode_head(self):
        """
        encode bytes into  Signal vars.
        """
        qq = b"qq"
        qq += self.signal_type
        qq += self.hex2bytes(self.qid, 2)
        qq += self.int2bytes(self.data_length, 2)
        self.header = qq

    def encode(self):
        self.encode_head()

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
        self.signal_type = b"a"
        super().__init__(data)
        self.break_starts_in = 0  # ticks until adbreak start
        self.splice_points = deque()  # splice signals included in adbreak
        self.data = data

    def decode(self):
        super().decode(self.data)
        self.break_starts_in = self.seconds(self.data[7:11])
        data = self.data[11:]
        while data:
            splice_point, data = qqheader()
            splice_point.decode()
            self.splicepoints.append(splice_point)


class ABTSignal(Signal):
    """
    ABTSignal AdBreak Terminate Signal
    Used to return early from an Ad Break.

    @ break_stops_in  a 32 bit value on a 90k clock,
        ticks until an ad break is terminated.
        a value of 0 indicates immediate terminate.
    """

    def __init__(self, data=None):
        self.signal_type = b"t"
        super().__init__(data)
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
        qqbase = super().encode()
        qq = self.seconds2bytes(self.break_stops_in, 4)
        self.data = qqbase + qq
        return self.data


class SpliceSignal(Signal):
    """
    SpliceSignal Class
    """

    def __init__(self, data=None):
        self.signal_type = b"s"
        super().__init__(data)
        self.sap_type = None
        self.cw_index = None
        self.tier = None
        self.break_duration = 0
        self.compliance_flag = None
        self.descriptors = []
        self.data = data

    def decode(self):
        """
        decode bytes into SpliceSignal vars.
        """
        super().decode()
        self.sap_type = self.hex(self.data[7])
        self.cw_index = self.hex(self.data[8])
        self.tier = self.hex(self.data[9:11])
        self.break_duration = self.seconds(self.data[11:15])
        self.compliance_flag = self.data[15]
        # pass anything left to unroll_descriptors()
        self.unroll_descriptors(self.data[16:])

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
        qqbase = super().encode()
        qq = self.hex2bytes(self.sap_type, 1)
        qq += self.hex2bytes(self.cw_index, 1)
        qq += self.hex2bytes(self.tier, 1)
        qq += self.seconds2bytes(self.break_duration, 4)
        qq += self.int2bytes(self.compliance_flag, 1)
        qq += self.roll_descriptors()
        self.data = qqbase + self.int2bytes(self.section_length, 2) + qq
