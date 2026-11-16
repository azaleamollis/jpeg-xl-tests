import sys
import os
sys.path.append(os.path.expandvars(r"%APPDATA%\Python\Python314\site-packages"))
import py7zr
py7zr.SevenZipFile(sys.argv[1]).extractall(sys.argv[2])
