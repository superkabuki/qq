# `qque`  is a shorthand SCTE-35 

* __No PTS__ hardcoded in  __qque__  Signals.
  * __SCTE-35 PTS is a big problem__ for a lot of people and __it's unnecessary__.
  * With __qque__, __it doesn't matter if the PTS changes__, the packet is still at the splice point, no need to adjust it.
  * __Splice Point is determined by location not the time value, however you can use PTS, or PCR, or Time from start to reference qque Signals__,
  * __Wall Clock Time Is Not Accurate with Streaming__,
      * 1 minute of video will take at least 1 minute to play, never less.
      * Even fractional seconds add up and cause drift      
* The __AdBreakSignal__ is inserted before the splice point.
* The __SpliceSignal__ is inserted at the splice point, and are __always Splice Immediate__
* The __ABTSignal__ _(Ad Break Terminate)_ can be used to return early from an ad break.
* __Descriptors__ and __Upids__ are included with the __SpliceSignal__
* All Signals have a unique 16 bit qid.
* __All time measurements are ticks on a 90k clock.__ 
* __All qque vars are byte aligned, no bits.__
* __qque Signals have No conditionally set vars__.
* 
* The same for HLS and DASH. 
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
    "startmark": 'qque',   b'qque'
    "signal_type" :0x62,   b'b'
    "qid: 0x39,           b'\x009'
    "break_starts_in" = 450000,  b'\x00\x06\xdd\xd0'

    "breaks" = {0x41: 5400000,    b'\x00A':b'\x00Re\xc0'
                0x42:2800000,     b'\x00B':b'\x00*\xb9\x80'
                0x43 : 11475000,   b'\x00C':b'\x00\xaf\x188'
} 
```
* To encode put it all together
```js
b'qqueb\x009\x00\x06\xdd\xd0\x00A\x00Re\xc0\x00B\x00*\xb9\x80\x00C\x00\xaf\x188'
```
* decode
```py3
>>>> startmark =qque[0:4]
>>>> signal_type=hex(qque[4])
qid = hex(int.from_bytes(qque[5:7], byteorder="big"))
>>>> bsn=qque[7:11]
>>>> break_start_in=int.from_bytes(bsn,byteorder="big")
>>>> idx=11
>>>> breaks={}
>>>> end =len(qque)
>>>> while idx < end
....     qid= qque[idx:idx+2]
....     idx+=2
....     dur=qque[idx:idx+4]
....     duration=int.from_bytes(dur,byteorder="big")
....     idx +=4
....     breaks[qid]= duration
>>>> print("\nstartmark ", startmark, "\nsignal_type ",signal_type,"\nq\
id ", qid, '\nbreak_start_in ', break_start_in, '\nbreaks', breaks)

startmark  b'qque' 
signal_type  0x62 
qid  0x39
break_start_in  450000 
breaks {b'\x00A': 5400000, b'\x00B': 2800000, b'\x00C': 11475000}
>>>> 
```

``
#    AdBreakSignal:

   * __startmark__ always __b'qque'__ always  __4 bytes__

   * __signal_type__ always __0x0a__ indicates AdBreakSignal __1 byte__
    
   * __qid__  qque id for this Signal __2 bytes__
    
   * __break_starts_in__  The number of ticks until the ad break starts, 4 bytes
       * this covers preroll. 450000 / 90000 = 5 seconds from now. 
       
  * __breaks__ is a map of  __qid__ and __brake_duration__ of the individual ads. __6 bytes each__  
     

b'qque'+ b'\x0a+b'\x009'+ b'\x00\x06\xdd\xd0'

 
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
```
#### SpliceSignal is ALWAYS splice immediate.
       
* __startmark__ always __b'qque'__ always  __4 bytes__ 
* __signal_type__ always __0x0b__ indicates a __SpliceSignal__ always __1 byte__
* __qid__ - Unique identifier for a specific Signal __2 bytes__
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
```js
 "ABTSignal"{
    "startmark": 'qque', 
    "signal_type" :0x0c, 
    "qid": 0x45,
    "break_stops_in": 0,
} 

* __startmark__ always __b'qque'__ always  __4 bytes__ 
* __signal_type__ always __0x0c__ indicates an __ ABTSignal__ always __1 byte__```
* __qid__ - Unique identifier for a specific Signal __2 bytes__
* __break_stops_in__ 90k clock ticks until an ad break is terminated. a value of 0 indicates immediate terminate.
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
