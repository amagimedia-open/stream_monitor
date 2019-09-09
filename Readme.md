
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


## Using tsduck to inert scte in a given mpegts file

1. Start docker and mount the input ts file and xml as shown below.

```
docker run -it --rm -v /home/amagi/TEST_ATPRG_IRNM1NLN.ts:/data/test.ts -v /home/amagi/scte.xml:/data/scte.xml -v /tmp/:/data/ shashibanger/strmmon:1.0 bash
```

2. Inside the docker run the following command to insert scte

```
tsp -I file /data/test.ts -P pmt --add-programinfo-id 0x43554549 --add-pid 6000/0x86 -P regulate -b 30000000 -P pcrextract -P spliceinject --service 1 --files '/data/scte.xml' -O file /data/o.ts
```

3. An example scte file data is shown below.

```
<?xml version="1.0" encoding="UTF-8"?>
<tsduck>
 <splice_information_table>
 <splice_insert splice_event_id="100" unique_program_id="1" out_of_network="true" pts_time="0x5532f0"/>
 </splice_information_table>
 <splice_information_table>
 <splice_insert splice_event_id="100" unique_program_id="1" out_of_network="false" pts_time="0x7e65d0"/>
 </splice_information_table>
</tsduck>
```

4. Check if scte packets are there
```
tsp -I file /data/o.ts -P filter --pid 6000 -O file /tmp/scte.ts
```

5. Extract scte
```
tsp -I file /data/o.ts -P pcrextract --scte35 --log -O drop 2> /tmp/o.txt
```
