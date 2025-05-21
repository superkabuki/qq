# quick35
__quick35__ is a replacement for SCTE-35 

* __Biggest__ change is no PTS in __quick35__ data.
* __quick35__ PTS is determined by packet PTS,  
* SCTE-35 PTS is a big problem for a lot of people and it's unnecessary.
* Everything is splice immediate with __quick35__.
* The __quick35__ packet is inserted at the splice point.
  * Even if the PTS changes, the packet is still at the splice point, no need to adjust it.
  * The same for HLS and DASH. 
* People also struggle with bits, __SpliceSignal__ and __AdBreakSignal__ vars are in bytes.

* For now, leave descriptors and upids as is, 

* Replace info section and commands with __SpliceSignal__

* Add __AdBreakSignal__

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

   * __table_id__ always __0xfc__   __1 byte__

   * __signal_type__ always __0x1b__ indicates AdBreakSignal __1 byte__
    
   * __adbreak_id__  Unique id for this AdBreakSignal __2 bytes__
    
   * __break_starts_in__  The number of seconds until the ad break starts, 2 bytes
       * this covers preroll. 5 means the ad break begins 5 seconds from now. 
       
  * __breaks__ is a map of  __unique_splice_id__ and __brake_duration__ of the individual ads. __6 bytes each__  
    
  * __note__ 32 bytes of data and /or padding for private data. __32 bytes__
 
  * __crc32__ __4 bytes__
 
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
* __section_length__: __2 bytes__
* __sap_type__ is __1 byte__
* __cw_index__ is __1 byte__
* __tier__ is  __2 bytes__
* __break duration__ is in seconds __4 bytes__ 
             
* __A break_duration greater than 0 means  out_of_network_indicator = True and duration flag = True__
* __A break_duration  equal to zero means out_of_network_indicator = False and duration flag = False__
* __splice_id__ - Unique identifier for a specific SpliceSignal __2 bytes__
* __compliance_flag__ is  __1 byte__
* __descriptor_loop_length__ is  __2 bytes__
* __note__  private data  and/or padding __32 bytes__
* Descriptors
* __crc32__ is __4 bytes__

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
