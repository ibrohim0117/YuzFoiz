from django.core.exceptions import ValidationError

MAX_IMAGE_SIZE_MB = 50


def validate_image_size(file):
    """Rasm hajmi MAX_IMAGE_SIZE_MB dan oshmasligi kerak."""
    max_bytes = MAX_IMAGE_SIZE_MB * 1024 * 1024
    if file.size > max_bytes:
        raise ValidationError(
            f"Rasm hajmi {MAX_IMAGE_SIZE_MB} MB dan oshmasligi kerak "
            f"(yuklangan: {file.size / (1024 * 1024):.2f} MB)."
        )
