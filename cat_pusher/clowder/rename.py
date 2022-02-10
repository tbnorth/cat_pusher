"""
List all the names in a dataset as
  ["name", "name"],
paste into renames list and edit second name to perform renaming.
"""
import requests
from clowder import ClowderRemote

renames = [
    ["old_name", "new_name"],
]

remote = ClowderRemote()

for from_, to in renames:
    file_id = remote.file_id(from_)
    if not file_id:
        continue
    url = remote.path["host"] + "api/files/%s/filename" % file_id
    params = dict(key=remote.path["key"])
    data = dict(name=to)
    response = requests.put(url, params=params, json=data)
    response.raise_for_status()

url = remote.path["host"] + "api/datasets/%s/listAllFiles" % remote.path["dataset_id"]
params = dict(key=remote.path["key"])
response = requests.get(url, params=params)
for result in response.json():
    print(f"[\"{result['filename']}\", \"{result['filename']}\"],")