"""Move duplicates in done.json to alternate dataset"""
import json

import requests
from clowder import ClowderRemote

ALT_DS = "6582f9b4e4b063812d5a0ae2"
SRC_FOLDER = "620278d7e4b039b22c797d87"

done = json.load(open("done.json"))
keep = set(i.get("keep") for i in done.values())
print(f"Keeping {len(keep)} / {len(done)}")
remote = ClowderRemote()
params = {"key": remote.path["key"]}
for drop in done.values():
    for file_id in drop["delete"]:
        assert file_id not in keep
        url = (
            f'{remote.path["host"]}'
            f"api/datasets/{ALT_DS}/moveToDataset/{SRC_FOLDER}/{file_id}"
        )
        print(url)
        response = requests.post(url, params=params)
        try:
            response.raise_for_status()
        except Exception:
            print("FAILED")
            # raise
