import importlib
import os
import time

remote = os.environ["CPSH_REMOTE"].split("://", 1)[0]
remote = importlib.import_module(f"{remote}.{remote}").cp_remote()


def check() -> None:
    copied = 0
    deleted = 0
    for filepath in remote.local_files():
        print(time.asctime())
        print(filepath)
        if not remote.file_exists(filepath):
            print(f"Copying {filepath.stat().st_size:,} to remote.")
            remote.copy_file(filepath)
            copied += 1
            time.sleep(5)  # let remote catch up
        verified = remote.verify_file(filepath)
        if verified and remote.get_env("CPSH_DELETE") == "Y":
            print(f"Verified remote {filepath}, deleting local")
            filepath.unlink()
            deleted += 1
        else:
            print("Not verified.")
    print(f"Copied {copied}, deleted {deleted}")


while True:
    check()
    print(time.asctime())
    print("Sleeping", remote.get_env("CPSH_INTERVAL"), "minutes")
    time.sleep(60 * int(remote.get_env("CPSH_INTERVAL")))
