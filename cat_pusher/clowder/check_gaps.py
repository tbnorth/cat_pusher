"""Check for time gaps in rename.py output"""
import re
import sys
from collections import namedtuple
from datetime import datetime

Row = namedtuple("Row", "name dupename size created id")
filenames = []
for line in sys.stdin:
    if line.startswith("#"):
        continue
    line = Row._make(eval(line))
    filenames.append(line.name)
# print(len(filenames))
regex = re.compile(r"\d{8}_\d{4}\.mp4")
filenames = [i for i in filenames if regex.match(i)]
# print(len(filenames))
filenames.sort()
for row in range(1, len(filenames)):
    fname = filenames[row - 1]
    t0 = fname[:4], fname[4:6], fname[6:8], fname[9:11], fname[11:13]
    t0 = datetime(*list(map(int, t0)))
    fname = filenames[row]
    t1 = fname[:4], fname[4:6], fname[6:8], fname[9:11], fname[11:13]
    t1 = datetime(*list(map(int, t1)))
    diff = t1 - t0
    if diff.total_seconds() > 20 * 60:
        print(t0, t1, diff)
