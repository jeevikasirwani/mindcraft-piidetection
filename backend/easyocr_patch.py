import PIL.Image
import sys

# Patch PIL.Image to add ANTIALIAS for compatibility
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

# Monkey patch the Image module
sys.modules['PIL.Image'].ANTIALIAS = PIL.Image.Resampling.LANCZOS 