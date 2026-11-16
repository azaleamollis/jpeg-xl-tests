import sys
import os
sys.path.append(os.path.expandvars(r"%APPDATA%\Python\Python314\site-packages"))
import imagecodecs as ic, numpy as np
print(ic.cms_profile.__doc__); print(ic.cms_transform.__doc__)
p=ic.cms_profile('srgb'); print(type(p), len(p))
print(ic.cms_info(p) if True else '')
