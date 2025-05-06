from PIL import Image
import io

def load_image(image_bytes_io):
    return Image.open(image_bytes_io).convert("RGB")
