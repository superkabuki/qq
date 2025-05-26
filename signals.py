"""
Signals

    Signal,
        AdBreakSignal
        SpliceSignal
        ABTSignal

"""

NTK = 90000


class Signal:
    """
    Signal is the base class for AdBreakSignal, SpliceSignal and ABTSignal.
    """

    def __init__(self):
        self.startmark = None
        self.signal_type = None
        self.qid = None

    def decode(self, bites):
        """
        decode bytes into Signal vars.
        """
        self.startmark = bites[0:4]
        self.signal_type = hex(bites[4])
        self.qid = self.hex(bites[5:7])

    def encode(self):
        """
        encode bytes into  Signal vars.
        """
        qq = b"qque"
        qq += self.int2bytes(self.signal_type, 1)
        if self.qid:
            qq += self.hex2bytes(self.qid, 2)
            return qq
        print("qid required")
        return False

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


class ABTSignal(Signal):
    """
    ABTSignal AdBreak Terminate Signal
    Used to return early from an Ad Break.

    @ break_stops_in  a 32 bit value on a 90k clock,
        ticks until an ad break is terminated.
        a value of 0 indicates immediate terminate.
    """

    def __init__(self):
        super().__init__()
        self.break_stops_in = 0

    def decode(self, bites):
        """
        decode bytes into ABTSignal vars.
        """
        super().decode(bites)
        self.break_stops_in = self.seconds(bites[7:11])

    def encode(self):
        """
        encode  ABTSignal vars into bytes
        """
        qqbase = super().encode()
        qq = self.seconds2bytes(self.break_stops_in, 4)
        return qqbase + qq


class SpliceSignal(Signal):
    """
    SpliceSignal Class
    """

    def __init__(self):
        super().__init__()
        self.section_length = 0
        self.sap_type = None
        self.cw_index = None
        self.tier = None
        self.break_duration = 0
        self.compliance_flag = None
        self.descriptors = []

    def decode(self, bites):
        """
        decode bytes into SpliceSignal vars.
        """
        super().decode(bites)
        self.section_length = self.int(bites[7:9])
        self.sap_type = self.hex(bites[9])
        self.cw_index = self.hex(bites[10])
        self.tier = self.hex(bites[11:13])
        self.break_duration = self.seconds(bites[13:17])
        self.compliance_flag = bites[17]
        # we don't need length, pass anything left to unroll_descriptors()
        self.unroll_descriptors(bites[18:])

    def unroll_descriptors(self, bites):
        """
        unroll_descriptors decode descriptors from bites
        """
        idx = 0
        bytelen = len(bites)
        while idx < bytelen:
            dtype = bites[idx]
            dlength = bites[idx + 1]
            idx += 2
            dbytes = bites[idx : idx + dlength]
            idx += dlength
            descriptor = descriptor_map[dtype](dbytes)
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
        return qqbase + self.int2bytes(self.section_length, 2) + qq
