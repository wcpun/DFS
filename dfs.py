from fs.memoryfs import MemoryFS
from fs.osfs import OSFS
import sys

dfs = MemoryFS()
dfs.makedir('test')
dfs.makedir('foo')

for path, info in dfs.walk.info(max_depth=1):
    if info.is_dir:
        print("[dir] {}".format(path))
    else:
        print("[file] {}".format(path))
