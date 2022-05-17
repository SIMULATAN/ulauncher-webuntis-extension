import re
from pathlib import Path

from PIL import Image


def save_image_hex(name, hexcolor):
    im = Image.new("RGB", (100, 100), hexcolor)
    Path(name).parent.mkdir(parents=True, exist_ok=True)
    im.save(name)


def boldify(query, inpt):
    return re.sub(r"(" + query + ")", r"<b>\g<0></b>", inpt, flags=re.IGNORECASE)
