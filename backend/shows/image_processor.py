from io import BytesIO

from django.core.files.base import ContentFile
from django.db.models.fields.files import ImageFieldFile
from PIL import Image, ImageOps


def process_show_image(
    image_field: ImageFieldFile, max_width: int, quality: int = 65, crop: bool = True
) -> ContentFile:
    """Crop to specific ratio, resize, and covert to webp for maximum performance."""
    img = Image.open(image_field)
    img = ImageOps.exif_transpose(img)  # respect camera rotation
    img = img.convert("RGB")

    # crop to target ratio (center crop)
    if crop:
        target_w, target_h = 1, 1
        current_ratio = img.width / img.height
        target_ratio = target_w / target_h

        if current_ratio > target_ratio:
            new_width = int(img.height * target_ratio)
            left = (img.width - new_width) // 2
            img = img.crop((left, 0, left + new_width, img.height))

        else:
            new_height = int(img.width / target_ratio)
            top = (img.height - new_height) // 2
            img = img.crop((0, top, img.width, top + new_height))

    if img.width > max_width:
        new_height = int(max_width * img.height / img.width)
        img = img.resize((max_width, new_height), Image.LANCZOS)

    buffer = BytesIO()
    img.save(buffer, format="WEBP", quality=quality, method=6)

    return ContentFile(buffer.getvalue())
