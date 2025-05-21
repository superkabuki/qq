# quick35
__quick35__ is a replacement for SCTE-35 

* Biggest change is no PTS.
 
* SCTE-35 PTS is a big problem for a lot of people and it's unnecessary.
* Everything is splice immediate with __quick35__.
* __quick35__ PTS is determined by packet PTS, The __quick35__ packet is inserted at the splice point.
  * Even if the PTS changes, the packet is still at the splice point, no need to adjust it.
  * The same for HLS and DASH. 
* People also struggle with bits, __SpliceSignal__ and __AdBreakSignal__ vars are in bytes.

* For now, leave descriptors and upids as is, 

* Replace info section and commands with SpliceSignal

* Add AdBreakSignal

* Sidecar files can be used or data can be embedded.

# AdBreakSignal  

* announces an upcoming ad break, and the breaks contained.

### How to detect: 

* first two bytes of payload are __b'\xfc\x1b'__
  
```js
 "AdBreakSignal"{
    "table_id": 0xfc, 
    "signal_type" :0x1b, 
    "adbreak_id: 0x39, 
    "break_starts_in" = 5,  
    "breaks" = {0x00001: 60.00, 
                0x00002:30.00, 
                0x00003 : 127.5},
    "note": "32 bytes of storage\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"   
    "crc32": 0x123457c,
} 
```
#    AdBreakSignal:

    * table_id always 0xfc 1 byte

    * signal_type always 0x1b indicates AdBreakSignal 1 byte
    
    * adbreak_id  Unique id for this AdBreakSignal 2 bytes
    
    * break_starts_in  The number of seconds until the ad break starts, 2 bytes
       * this covers preroll. 5 means the ad break begins 5 seconds from now. 
       
    * breaks unique_splice_id and duration of the individual ads. 6 bytes each  
    
    * note 32 bytes of data and /or padding for private data.
 
    * crc32 4 bytes
 
### Xml 
 
```xml
    <AdBreakSignal tableId=0xfc signalType=0x1b breakStartsIn=5>
        <Break uniqueSpliceId=0x000001 breakDuration=60/>
        <Break uniqueSpliceId=0x000002 breakDuration=30/>    
        <Break uniqueSpliceId=0x000003 breakDuration=127.50/>
        <Note>32 bytes of storage</Note>
    </AdBreakSignal>
```

# SpliceSignal.

###  How to detect: 

* first two bytes of payload are __b'\xfc\x0d'__

```js
"SpliceSignal": {
        "table_id": "0xfc", # 1 byte
        "signal_type: 0x0d,  #1 byte
        "section_length: 72, # 2 bytes
        "sap_type": "0x03",    # 1 byte
        "cw_index": "0x00", # 1 byte       What does this even mean?
        "tier": "0x0fff",  # 2 bytes
        "break_duration": 119.23   # 4 bytes # 
        "splice_id": 0x0001, # 2 bytes Unique identifier for a specific SpliceSignal
        "compliance_flag": True, # 1 byte
        "descriptor_loop_length": 26, 2 bytes
        "note": "private data and/or padding" # 32 bytes
        "crc32": "0xa6ac3c8d"   # 4 bytes
    }
```
#### SpliceSignal is ALWAYS splice immediate.
       
* table_id always 0xfc 1 byte
* signal_type always 0x0d indicates a SpliceSignal 1 byte
* section_length: 2 bytes
* sap_type 1 byte
* cw_index 1 byte
* tier 2 bytes
* break duration is seconds 4 bytes 
             
* __A break_duration greater than 0 means  out_of_network_indicator = True and duration flag = True__
* __A break_duration  equal to zero means out_of_network_indicator = False and duration flag = False__
* splice_id - Unique identifier for a specific SpliceSignal 2 bytes
* compliance_flag  1 byte
* descriptor_loop_length  2 bytes
* note  private data  and/or padding 32 bytes
* Descriptors
* crc32 4 bytes

### Xml 
```xml
    <SpliceSignal sap_type= 0x03 cwIndex= 0x00 tier= 0x0fff ComplianceFlag= "true">
        <UniqueSpliceId> 0x0001</UniqueSpliceId>
        <BreakDuration>119.23</BreakDuration> 
        <Note>"A Note"</Note>
        <AvailDescriptor providerAvailId="12"/>
        <AvailDescriptor providerAvailId="13"/>
        <AvailDescriptor providerAvailId="14"/>
        <AvailDescriptor providerAvailId="15"/>
   </SpliceSignal>
```
