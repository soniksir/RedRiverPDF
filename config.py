import os
from PIL import Image

# Poppler yolu
POPPLER_PATH = os.path.join(os.path.dirname(__file__), "poppler", "Library", "bin")

# Pillow sürüm uyumu
try:
    RESAMPLE_MODE = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE_MODE = Image.LANCZOS

