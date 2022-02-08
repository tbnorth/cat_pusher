import os
import time
from hashlib import sha256
from pathlib import Path


class CatPusherRemote:
    def __init__(self):
        self.local_path = Path(self.get_env("CPSH_LOCAL"))
        self.remote_spec = self.get_env("CPSH_REMOTE").split("://", 1)[-1]

    def relative_path(self, filepath: Path):
        return filepath.relative_to(self.local_path).parent

    @staticmethod
    def get_env(variable):
        return os.environ.get(variable)

    @classmethod
    def local_files(cls):
        """Files to consider for processing."""
        min_size = int(cls.get_env("CPSH_MIN_SIZE"))
        max_modified = time.time() - 60 * int(cls.get_env("CPSH_DELAY"))
        for filepath in Path(cls.get_env("CPSH_LOCAL")).glob("**/*"):
            if not filepath.is_file():
                continue
            stat = filepath.stat()
            if stat.st_size < min_size:
                print(f"{filepath} - too small")
                continue
            if stat.st_mtime > max_modified:
                print(
                    f"{filepath} - {(stat.st_mtime-max_modified)/60:0.1f} min. too new"
                )
                continue
            yield filepath

    @staticmethod
    def hash_file(frompath: Path, hash=None):
        if hash is None:
            hash = sha256()
        else:
            hash = hash()
        with frompath.open("rb") as in_:
            while len(data := in_.read(10_000_000)) > 0:
                hash.update(data)
        return hash.hexdigest()
