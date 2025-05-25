'''
"SpliceSignal": {
        "startmark": "qque", # 4 bytes
        "signal_type: 0x0b,  #1 byte
        "qid": 0x41, # 2 bytes Unique identifier for a specific SpliceSignal
        "section_length: 72, # 2 bytes
        "sap_type": "0x03",    # 1 byte
        "cw_index": "0x00", # 1 byte       What does this even mean?
        "tier": "0x0fff",  # 2 bytes
        "break_duration": 10730700   # 4 bytes # 
        "compliance_flag": True, # 1 byte
        "descriptor_loop_length": 26,#  2 bytes
        "crc32": "0xa6ac3c8d"   # 4 bytes
    }
'''

class SpliceSignal:
    def __init__(self):
        self.startmark =None
        self.signal_type= 0x0b
        qid = None
        self.section_length = 0
        self.sap_type = None
        self.cw_index= None
        self.tier = None
        self.break_duration=0
        self.compliance_flag=None
        self.descriptor_loop_length=0
        self.crc32 = None


    def hex(self,bites):
        """
        hex return bites as a hex value prefixed by 0x
        """
        return hex(self.int(bites))

    def int(self,bites):
        """
        int return bites as an integer
        """
        return int.from_bytes(bites, byteorder='big')

    def seconds(self,bites):
        """
        seconds return bites as seconds from a 90k clock
        """
        90k = 90000
        return self.int(bites) /90k

    def decode(self,bites):
        self.startmark=bites[0:4]
        self.signal_type=hex(bites[4])
        self.qid=self.hex(bites[5:7])
        self.section_length=self.int(bites[7:9])
        self.sap_type=bites[9]
        self.cw_index= bites[10]
        self.tier = self.hex(bites[11:13])
        self.break_duration = self.seconds(bites[13:17])
        self.compliance_flag=bites[17]
        self.descriptor_loop_length=self.int(bites[18:20])
        
















        
