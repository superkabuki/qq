# `qque`  is a replacement for SCTE-35 

* __Biggest__ change is no PTS in __qque__  Signals.
* __qque__ PTS is determined by packet location,
* Even if the PTS changes, the packet is still at the splice point, no need to adjust it.
* SCTE-35 PTS is a big problem for a lot of people and it's unnecessary.
* Everything is splice immediate with __qque__ .
* The __AdBreakSignal__ is inserted before the splice point.
* The __SpliceSignal__ is inserted at the splice point.
* __Descriptors__ and __Upids__ are included with the __SpliceSignal__
* __AdBreakSignals__ and __SpliceSignals__ have a unique 16 bit qid.
* All time units are ticks on a 90k clock. 

* The same for HLS and DASH. 
* People also struggle with bits, __SpliceSignal__ and __AdBreakSignal__ vars are in bytes.

* For now, leave upids as is, 

* Replace info section and commands with __SpliceSignal__

* Add __AdBreakSignal__

* Sidecar files can be used or data can be embedded.

# AdBreakSignal  

* announces an upcoming ad break, and the breaks contained.

### How to detect: 

* first five bytes of payload are __b'qque\x0a'__
  
```js
 "AdBreakSignal"{
    "startmark": 'qque', 
    "signal_type" :0x0a, 
    "qid: 0x39, 
    "break_starts_in" = 450000,  
    "breaks" = {0x41: 5400000, 
                0x42:2800000, 
                0x43 : 11475000,
    "crc32": 0x123457c,
} 
```
#    AdBreakSignal:

   * __startmark__ always __b'qque'__ always  __4 bytes__

   * __signal_type__ always __0x0a__ indicates AdBreakSignal __1 byte__
    
   * __qid__  qque id for this Signal __2 bytes__
    
   * __break_starts_in__  The number of ticks until the ad break starts, 4 bytes
       * this covers preroll. 450000 / 90000 = 5 seconds from now. 
       
  * __breaks__ is a map of  __qid__ and __brake_duration__ of the individual ads. __6 bytes each__  
     
  * __crc32__ __4 bytes__
 
### Xml 
 
```xml
    <AdBreakSignal qid= 0x39 breakStartsIn=450000>
        <Break qid=0x40 breakDuration=540000/>
        <Break qid=0x41 breakDuration=280000/>    
        <Break qid=0x42 breakDuration=11475000/>
    </AdBreakSignal>
```

# SpliceSignal.

###  How to detect: 

* first five bytes of payload are __b'qque\x0b'__

```js
"SpliceSignal": {
        "startmark": "qque", # 4 bytes
        "signal_type: 0x0b,  #1 byte
        "section_length: 72, # 2 bytes
        "sap_type": "0x03",    # 1 byte
        "cw_index": "0x00", # 1 byte       What does this even mean?
        "tier": "0x0fff",  # 2 bytes
        "break_duration": 10730700   # 4 bytes # 
        "qid": 0x41, # 2 bytes Unique identifier for a specific SpliceSignal
        "compliance_flag": True, # 1 byte
        "descriptor_loop_length": 26,#  2 bytes
        "crc32": "0xa6ac3c8d"   # 4 bytes
    }
```
#### SpliceSignal is ALWAYS splice immediate.
       
* __startmark__ always __b'qque'__ always  __4 bytes__ 
* __signal_type__ always __0x0b__ indicates a __SpliceSignal__ always __1 byte__
* __qid__ - Unique identifier for a specific SpliceSignal __2 bytes__
* __section_length__: __2 bytes__
* __sap_type__ is __1 byte__
* __cw_index__ is __1 byte__
* __tier__ is  __2 bytes__
* __break duration__ is a a 90k clock (ticks) __4 bytes__           
   * __A break_duration greater than 0 means  out_of_network_indicator = True and duration flag = True__
   * __A break_duration  equal to zero means out_of_network_indicator = False and duration flag = False__

* __compliance_flag__ is  __1 byte__
* __descriptor_loop_length__ is  __2 bytes__
* Descriptors
* __crc32__ is __4 bytes__

### Xml 
```xml
    <SpliceSignal qid=0x43 sap_type= 0x03 cwIndex= 0x00 tier= 0x0fff ComplianceFlag= "true">
        <BreakDuration>10730700</BreakDuration>      
   </SpliceSignal>
```

# ABTSignal
* Ad Break Terminate Signal
* immediately return from Ad break



* __startmark__ always __b'qque'__ always  __4 bytes__ 
* __signal_type__ always __0x0b__ indicates a __SpliceSignal__ always __1 byte__```

# Descriptors

### RestrictdDescriptor

  *   delivery_not_restricted_flag is redundant
    
 ```js
{
"type": 0xaa,     # 1 byte
"length" 37, # 1byte
"web_delivery_allowed_flag" : True # 1 byte
"no_regional_blackout_flag" : True  # 1 byte
"archive_allowed_flag" :  True # 1 byte
device_restrictions : 0x02    # 1 byte
}
```
### SegmentDescriptor
```js
{
     type 0xbb, # 1 byte
     length 29, # 1 byte
     segment_type_message: " breakin'"   # from a table by segment_type_id
     segment_type_id = 0x33,       # 1 byte
     segment_upid_length: 19,      # 1 byte
     segment_upid_type = 0x05,     # 1byte
     segment_upid_type_name ="AirId"    # from a table by segment_upid_type
     segment_upid : b'I am the upid damn it!' # variable length bytes
}

```
