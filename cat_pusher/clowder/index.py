"""Make a simple HTML index of videos from output of rename.py.

["20220208_1249.mp4", "20220208_1249.mp4", 266379456],
"""

import calendar
import json
import re
import sys
from collections import defaultdict, namedtuple
from pathlib import Path

CSS = """
* { font-family: sans-serif; }
table.year > tbody > tr { vertical-align: top; }
td { width: 9ex; height: 4ex; }
.month {margin-right: 2em}
a { text-decoration: none; }
"""
HEAD = """
<html><head><style>
* { font-family: sans-serif; }
a {text-decoration: none; width: 4em;display: inline-block;}
</style></head><body>
"""
FOOT = "</body></html>"

files = []

for line in sys.stdin:
    try:
        files.append(json.loads(line.strip("\n ,"))[0])
    except json.decoder.JSONDecodeError:
        pass
RE = re.compile(
    r"(?P<year>\d\d\d\d)(?P<month>\d\d)(?P<day>\d\d)"
    r"_(?P<hour>\d\d)(?P<min>\d\d)\.mp4"
)
files = [i for i in files if RE.match(i)]
files = sorted(set(files))
days = defaultdict(list)
Video = namedtuple("Video", "file year month day hour min")
for file in files:
    m = RE.match(file)
    video = Video._make([file] + [int(m.group(i)) for i in Video._fields[1:]])
    days[(video.year, video.month, video.day)].append(video)


class VideoYear(calendar.HTMLCalendar):
    def formatmonth(self, year, month, **kwargs):
        self.month = month
        self.year = year
        return super().formatmonth(year, month, **kwargs)

    def formatday(self, date, dow):
        vids = days[(self.year, self.month, date)]
        link = ""
        if vids:
            link = f"<a href='{self.month:02d}.{date:02d}.html'>{date}</a>"
            with Path(f"{self.year}/{self.month:02d}.{date:02d}.html").open("w") as out:
                out.write(HEAD)
                out.write(f"<h2>{self.year}-{self.month:02d}-{date:02d}</h2>")
                for vid_i, vid in enumerate(vids):
                    href = (
                        "https://clowder.edap-cluster.com/search?query=name=="
                        + vid.file
                    )
                    if vid_i % 8 == 0:
                        out.write("<br/>")
                    out.write(
                        "<a target='_vid' "
                        f"href='{href}'>{vid.hour:02d}:{vid.min:02d}</a> "
                    )
                out.write(FOOT)

        return f"<td>{link}</td>"


vidyear = VideoYear()
Path("2022/index.html").write_bytes(vidyear.formatyearpage(2022))
Path("2022/calendar.css").write_text(CSS)
Path("2023/index.html").write_bytes(vidyear.formatyearpage(2023))
Path("2023/calendar.css").write_text(CSS)
