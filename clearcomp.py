import shutil
import os

os.chdir(os.path.dirname(__file__))

for ver in ["lin", "win", "mac"]:
    try:
        folder = f"compile-{ver}"
        shutil.rmtree(folder)
        os.mkdir(folder)
    except:
        pass