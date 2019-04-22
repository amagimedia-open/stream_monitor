"""
APplication to monito the incoming RTP stream and log errors and othe information
"""
import logging
import time
import logger
import shlex
import subprocess
import os
import sys

global log

class TsDuckOutAnalyze(object):
    def __init__(self):
        pass

    def analyze(self, line):
        print(line)


class StreamMon(object):
    def __init__(self):
        self.strm_recv_pid = None
        self.fifo_name = "/tmp/inp.ts"
        try:
            if not os.path.exists(self.fifo_name):
                os.mkfifo(self.fifo_name)
        except os.error as e:
            print(e)
            log.fatal(f"message=Could not open fifo {self.fifo_name}")
            sys.exit(1)
        self.tsduck_analyze = TsDuckOutAnalyze()


    def rtp_inp_to_fifo(self, port):
        cmd = f"rtpdump -F payload -o {self.fifo_name} 0.0.0.0/{port}"
        args = shlex.split(cmd)
        self.strm_recv_pid = subprocess.Popen(args)

    def tsduck_process(self):
        cmd = f"tsp  --max-input-packets 50 --max-flushed-packets 50 -t -I file {self.fifo_name} -P pcrextract --log  -P continuity -O drop"
        args = shlex.split(cmd)
        self.tsduck_pid = subprocess.Popen(args, stdout=subprocess.PIPE)
        for line in self.tsduck_pid.stdout:
            self.tsduck_analyze.analyze(line)


def main():
    inp_port = int(sys.argv[1])
    strm_mon = StreamMon()
    strm_mon.rtp_inp_to_fifo(inp_port)
    strm_mon.tsduck_process()
    while True:
        time.sleep(5)

if __name__ == "__main__":
    logger.logging_setup('.', 'strmmon')
    log=logging.getLogger('strmmon')
    main()
