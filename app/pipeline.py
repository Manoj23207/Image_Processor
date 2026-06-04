from PIL import Image
from typing import List

class FlipHorizontal:
    name = "flip_horizontal"
    def apply(self, img): return img.transpose(Image.FLIP_LEFT_RIGHT)

class FlipVertical:
    name = "flip_vertical"
    def apply(self, img): return img.transpose(Image.FLIP_TOP_BOTTOM)

class Grayscale:
    name = "grayscale"
    def apply(self, img):
        gray = img.convert("L")
        return gray.convert("RGB")

class RotateLeft:
    name = "rotate_left"
    def apply(self, img): return img.rotate(90, expand=True)

class RotateRight:
    name = "rotate_right"
    def apply(self, img): return img.rotate(-90, expand=True)

OPERATIONS = {
    "flip_horizontal": FlipHorizontal,
    "flip_vertical":   FlipVertical,
    "grayscale":       Grayscale,
    "rotate_left":     RotateLeft,
    "rotate_right":    RotateRight,
}

def process(image_path: str, operation_names: List[str], output_path: str) -> None:
    ops = []
    for name in operation_names:
        if name not in OPERATIONS:
            raise ValueError(f"Unknown operation: '{name}'")
        ops.append(OPERATIONS[name]())
    with Image.open(image_path) as img:
        img = img.copy()
    for op in ops:
        img = op.apply(img)
    fmt = "PNG" if output_path.endswith(".png") else "JPEG"
    img.save(output_path, format=fmt, quality=95)
