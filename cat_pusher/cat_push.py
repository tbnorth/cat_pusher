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
            size = filepath.stat().st_size
            print(f"Copying {size:,} to remote.")
            start = time.time()
            remote.copy_file(filepath)
            duration = time.time() - start
            print(f"{duration:.2f} seconds, {size / duration:,.0f} per second.")
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


print("=" * 20, "Start run", "=" * 20)
while True:
    check()
    print(time.asctime())
    print("-" * 20, "Sleeping", remote.get_env("CPSH_INTERVAL"), "minutes", "-" * 20)
    time.sleep(60 * int(remote.get_env("CPSH_INTERVAL")))
