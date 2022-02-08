import shutil
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
        return self.hash_file(frompath) == self.hash_file(self.dest_path(frompath))


cp_remote = OtherPath
