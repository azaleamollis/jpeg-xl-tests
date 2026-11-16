import sys
import os
sys.path.append(os.path.expandvars(r"%APPDATA%\Python\Python314\site-packages"))
import imagecodecs, numpy as np
print(imagecodecs.__version__, imagecodecs.LCMS2.available if hasattr(imagecodecs,'LCMS2') else 'no LCMS2 attr')
print([n for n in dir(imagecodecs) if 'cms' in n.lower()])
import PIL, PIL.features as f; print(PIL.__version__, f.version('jpg'), f.version('libpng'), f.version('lcms2'))
try:
    import oxipng; print('oxipng', oxipng.__file__)
except Exception as e: print('oxipng', e)
