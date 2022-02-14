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
        self.connector = pyclowder.connectors.Connector(
            None, None, max_retry=int(self.get_env("CPSH_RETRY", 10))
        )
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
        pyclowder.files.upload_to_dataset(
            connector=self.connector,
            datasetid=self.path["dataset_id"],
            filepath=frompath,
            folder_id=self.path["folder_id"],
            host=self.path["host"],
            key=self.path["key"],
        )

    def file_ids_list(self, frompath: str) -> list:
        params = dict(
            key=self.path["key"],
            resource_type="file",
            datasetid=self.path["dataset_id"],
            query=f"name=={frompath}",
        )
        url = self.path["host"] + "api/search"

        response = requests.get(url, params=params)
        response.raise_for_status()
        return [i for i in response.json()["results"] if i["name"] == frompath]

    def file_id(self, frompath: str) -> str:
        hits = self.file_ids_list(frompath)
        if len(hits) != 1:
            if len(hits) > 1:
                print(hits)
            return False
        return hits[0]["id"]

    def file_exists(self, frompath: Path) -> bool:
        return len(self.file_ids_list(frompath)) > 0

    def verify_file(self, frompath: Path) -> bool:
        """Sometimes multiple copies on server, so return True if ALL copies have same
        hash, checking *carefully*.
        """
        file_ids = self.file_ids_list(frompath.name)
        if not file_ids:
            return False
        true = 0
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
            metas = [
                i
                for i in response.json()
                if i.get("agent", {}).get("name", "").endswith("ncsa.file.digest")
            ]
            if len(metas) != 1:
                print("Found multiple metas.")
                return False
            if self.hash_file(frompath) != metas[0]["content"]["sha256"]:
                return False
            else:
                true += 1

        return true == len(file_ids)  # can't be otherwise but paranoid


cp_remote = ClowderRemote
