import shutil
from hashlib import sha256
from pathlib import Path

from cat_pusher import CatPusherRemote


class OtherPath(CatPusherRemote):
    def __init__(self):
        super().__init__()
        self.remote_path = Path(self.remote_spec).expanduser()

    def dest_path(self, frompath: Path) -> Path:
        return self.remote_path / self.relative_path(frompath) / frompath.name

    def copy_file(self, frompath: Path):
        dest = self.dest_path(frompath)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(frompath, dest)

    def verify_file(self, frompath: Path):
        hashes = []
        for path in frompath, self.dest_path(frompath):
            h256 = sha256()
            with path.open("rb") as in_:
                while len(data := in_.read(10_000_000)) > 0:
                    h256.update(data)
            hashes.append(h256.hexdigest())
        return hashes[0] == hashes[1]


cp_remote = OtherPath
