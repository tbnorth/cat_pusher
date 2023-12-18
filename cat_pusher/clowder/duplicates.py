import sys
from collections import defaultdict, namedtuple
from pathlib import Path

import requests

Row = namedtuple("Row", "name dupename size created id")


def get_files_from_log():
    files = defaultdict(list)
    total = 0
    waste = 0
    for line in sys.stdin:
        if line.startswith("#"):
            continue
        line = Row._make(eval(line))
        files[(line.name, line.size)].append(line)
    for name, size in files.keys():
        total += len(files[(name, size)]) * size
    files = {k: v for k, v in files.items() if len(v) != 1}
    for name, size in files.keys():
        print(name, size, len(files[(name, size)]))
        waste += (len(files[(name, size)]) - 1) * size
    return files, total, waste


files, total, waste = get_files_from_log()
print(f"{total:,}")
print(f"{waste:,}")


def de_dupe(file_ids):
    if not file_ids:
        return False
    true = 0
    local_hash = self.hash_file(frompath)
    no_meta = False
    for file_id in file_ids:
        file_id = file_id["id"]
        params = {"key": self.path["key"]}
        url = f'{self.path["host"]}' f"api/files/{file_id}/metadata.jsonld"
        response = requests.get(url, params=params)
        try:
            response.raise_for_status()
        except Exception:
            print(url)
            raise
        # (frompath.parent / "hash" / frompath.name).with_suffix(".json")
        # .write_text(     json.dumps(response.json(), indent=4)
        # )
        metas = [
            i
            for i in response.json()
            if i.get("agent", {}).get("name", "").endswith("ncsa.file.digest")
        ]
        if len(metas) == 0:
            print(f"Found NO metas: {frompath} - {file_id}")
            no_meta = True
        if len(metas) != 1:
            print(f"Found multiple metas: {frompath} - {file_id}")
        if any(i["content"]["sha256"] == local_hash for i in metas):
            true += 1
            print(f"Found match: {frompath} - {file_id}")
        else:
            print(f"NO match: {frompath} - {file_id}")
        # if self.hash_file(frompath) != metas[0]["content"]["sha256"]:
        #     return False
        # else:
        #     true += 1

    if true == 0 and no_meta:
        raise self.NoMetaDataError

    return true > 0
