import os
import importlib
remote = os.environ["CPSH_REMOTE"].split("://", 1)[0]
remote = importlib.import_module(f"{remote}.{remote}").cp_remote()

for filepath in remote.local_files():
    print(filepath)
    print(remote.dest_path(filepath))
    remote.copy_file(filepath)
    print("OK" if remote.verify_file(filepath) else "Verify FAILED")
