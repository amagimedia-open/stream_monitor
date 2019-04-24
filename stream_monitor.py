"""
APplication to monito the incoming RTP stream and log errors and othe information
"""
import os
import re
import logging
import time
import shlex
import subprocess
import sys
from dataclasses import dataclass
import pandas as pd
import logger

#global log

@dataclass
class PtsInfo:
    state: str # Can be 'priming' or 'steady'
    median_pts_diff: float
    last_out_pts: float
    pts_seq: pd.Series


class LogContinuityErr(object):
    @staticmethod
    def _parse_line(l):
        ret_dict = None
        m = re.search("PID: ([0-9x]*), missing: ([0-9]*)", l)
        if m is not None:
            ret_dict = dict(pid=int(m.group(1), 16), missing=int(m.group(2)))

        return ret_dict

    @staticmethod
    def  log_continuity(line):
        l_dict = LogContinuityErr._parse_line(line)
        if l_dict is not None:
            log.error(f"event=cc_error, pid={l_dict['pid']}, missing={l_dict['missing']}")

class PcrExtractAnalyze(object):
    def __init__(self):
        '''
        pts_dict is of the following type
        {
          pid_num -> PtsInfo
        }
        '''
        self.pts_dict = {}

    def _handle_new_pts(self, pid, pts):
        if pid in self.pts_dict:
            if (self.pts_dict[pid].state == 'priming'):
                pts_seq_duration = (self.pts_dict[pid].pts_seq.max() -
                                    self.pts_dict[pid].pts_seq.min())
                self.pts_dict[pid].pts_seq = self.pts_dict[pid].pts_seq.append(
                        pd.Series([pts/90000.0]), ignore_index=True)
                if (pts_seq_duration > 2.0):
                    self.pts_dict[pid].state = "steady"
                    self.pts_dict[pid].median_pts_diff = self.pts_dict[pid].pts_seq.diff().median()
                    self.pts_dict[pid].last_out_pts = self.pts_dict[pid].pts_seq.min()
            elif self.pts_dict[pid].state == 'steady':
                if self.pts_dict[pid].median_pts_diff < 0.5:
                    self.pts_dict[pid].pts_seq = self.pts_dict[pid].pts_seq.append(
                                                   pd.Series([pts/90000.0]),
                                                   ignore_index=True)
                    # Pid seems to be audio video data
                    min_pts = self.pts_dict[pid].pts_seq.min()
                    diff_wrto_last_pts = abs(min_pts - self.pts_dict[pid].last_out_pts)
                    self.pts_dict[pid].last_out_pts = min_pts
                    if diff_wrto_last_pts > (1.5 * self.pts_dict[pid].median_pts_diff):
                        print(min_pts, self.pts_dict[pid].last_out_pts)
                        log.error((f"event=pts_discontinuity, pid={pid},"
                                   f"diff={diff_wrto_last_pts}, "
                                   f"expected_diff={self.pts_dict[pid].median_pts_diff}"))
                    self.pts_dict[pid].pts_seq = self.pts_dict[pid].pts_seq.drop(
                            self.pts_dict[pid].pts_seq.idxmin())
        else:
            self.pts_dict[pid] = PtsInfo('priming', 0.0, pts, pd.Series())

    @staticmethod
    def _parse_line(line):
        '''
        Parses the pcrextract output and returns tuple (ts_type: "pts|pcr|dts", pid:int, pts: str)
        E.g line to parse:
        * 2019/04/23 08:29:29 - pcrextract: PID: 0x0814 (2068), PTS: 0x001080AB0, (0x0000F5280, 11,157 ms from start of PID)
        '''
        m = re.search("PID: ([0-9xA-Fa-f]*) \([0-9]*\), (PTS|DTS|PCR): ([0-9xA-Fa-f]*)", line)
        if m is not None:
            ret = (m.group(2), int(m.group(1), 16), int(m.group(3), 16))
        return ret




    def analyze_line(self, line):
        (ts_type, pid, pts) = PcrExtractAnalyze._parse_line(line)
        if ts_type == "PTS":
            self._handle_new_pts(pid, pts)





class TsDuckOutAnalyze(object):
    def __init__(self):
        self.pcr_ext_process = PcrExtractAnalyze()

    def get_log_type(self, line):
        l_type = None
        m = re.match("\* [0-9/]* [0-9:]* - ([A-Za-z0-9]*)", line)
        if m is not None:
            l_type = m.group(1)
        return l_type



    def analyze(self, line):
        ltype = self.get_log_type(line)
        if ltype is not None:
            if ltype == "continuity":
                LogContinuityErr.log_continuity(line)
            elif ltype == "pcrextract":
                self.pcr_ext_process.analyze_line(line)


class StreamMon(object):
    def __init__(self):
        self.strm_recv_pid = None
        self.fifo_name = "/tmp/inp.ts"
        self.tsduck_pid = None
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
        self.tsduck_pid = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        count=0
        for line in self.tsduck_pid.stderr:
            self.tsduck_analyze.analyze(line.decode())
            count += 1
            if count > 500:
                print("All izz well")
                count = 0


def main():
    inp_port = int(sys.argv[1])
    strm_mon = StreamMon()
    strm_mon.rtp_inp_to_fifo(inp_port)
    strm_mon.tsduck_process()
    while True:
        time.sleep(5)

if __name__ == "__main__":
    global log
    logger.logging_setup('.', 'strmmon')
    log = logging.getLogger('strmmon')
    main()
