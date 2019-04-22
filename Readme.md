
# Stream Monitor

A container which when run monitors a live AV stream and logs information and errors.

Live streaming formats supported
- RTP carrying mpeg2ts


## Stream analysis for rtp input

Stream analysis involves the following

1. Using rtpdump we redirect the ts payload to a fifo.
   rtpdump -F payload -o /tmp/1.ts 0.0.0.0/31000
   
2. Using tsduck we extract live pcr, pts values. 
   tsp  --max-input-packets 50 --max-flushed-packets 50 -t -I file /tmp/1.ts -P pcrextract --log  -P continuity -O drop
   
3. The output of step 2 is analyzed using stream_monitor.py. PTS dicontinuity, CC discontinuity errors will be logged.
