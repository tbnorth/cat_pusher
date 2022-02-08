from pathlib import Path
from urllib.parse import urlparse

import pyclowder.connectors
import pyclowder.files
import requests

from cat_pusher import CatPusherRemote


class ClowderRemote(CatPusherRemote):
    def __init__(self):
        super().__init__()
        self.remote_spec = urlparse(self.get_env("CPSH_REMOTE"))
        assert self.remote_spec.scheme == "clowder"
        self.connector = pyclowder.connectors.Connector(None, None)
        self.path = dict(
            host="https://" + self.remote_spec.hostname + "/",
            key=self.remote_spec.username,
            dataset_id=self.remote_spec.path.strip("/").split("/")[-1],
            folder_id=self.remote_spec.fragment.split("=")[-1],
        )

    def dest_path(self, frompath: Path) -> Path:
        # FIXME: not accurate
        return self.remote_spec.path / self.relative_path(frompath) / frompath.name

    def copy_file(self, frompath: Path):
        return
        pyclowder.files.upload_to_dataset(
            connector=self.connector,
            datasetid=self.path["dataset_id"],
            filepath=frompath,
            folder_id=self.path["folder_id"],
            host=self.path["host"],
            key=self.path["key"],
        )

    def file_id(self, frompath: Path) -> str:
        params = {"key": self.remote_spec.username}
        url = (
            f'{self.path["host"]}'
            f'api/datasets/{self.path["dataset_id"]}/listAllFiles'
        )

        response = requests.get(url, params=params)
        response.raise_for_status()
        hits = [i for i in response.json() if i["filename"] == frompath.name]
        if len(hits) != 1:
            return False
        return hits[0]["id"]

    def verify_file(self, frompath: Path) -> bool:
        params = {"key": self.remote_spec.username}
        file_id = self.file_id(frompath)
        url = f'{self.path["host"]}' f"api/files/{file_id}/metadata.jsonld"
        response = requests.get(url, params=params)
        response.raise_for_status()
        metas = [
            i
            for i in response.json()
            if i.get("agent", {}).get("name", "").endswith("ncsa.file.digest")
        ]
        if len(metas) != 1:
            return False
        return self.hash_file(frompath) == metas[0]["content"]["sha256"]


cp_remote = ClowderRemote
