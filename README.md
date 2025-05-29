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
* All Signals have a unique 16 bit qqid.
* __All time measurements are ticks on a 90k clock.__ 
* __qque Signals have No conditionally set vars__.

* Replace info section and commands with __SpliceSignal__

* Add __AdBreakSignal__

* Sidecar files can be used or data can be embedded.

# AdBreakSignal  

* announces an upcoming ad break, and the breaks contained.


# SpliceSignal.

# ABTSignal
* Ad Break Terminate Signal
* immediately return from Ad break

# Descriptors

### RestrictdDescriptor


### SegmentDescriptor
