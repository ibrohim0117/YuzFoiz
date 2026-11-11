from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from .validators import validate_image_size


class User(AbstractUser):
    class ImageStatus(models.TextChoices):
        PENDING = 'pending', 'Kutilmoqda'
        APPROVED = 'approved', 'Tasdiqlangan'
        REJECTED = 'rejected', 'Bekor qilingan'

    image = models.ImageField(
        'Rasm',
        upload_to='users/images/%Y/%m/',
        validators=[validate_image_size],
        blank=True,
        null=True,
    )
    image_status = models.CharField(
        'Rasm holati',
        max_length=10,
        choices=ImageStatus.choices,
        default=ImageStatus.PENDING,
        db_index=True,
    )
    rejection_reason = models.TextField(
        'Bekor qilish sababi',
        blank=True,
        help_text="Holat 'Bekor qilingan' bo'lsa majburiy. Foydalanuvchiga ko'rsatiladi.",
    )

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'

    def __str__(self):
        return self.get_full_name() or self.username

    # --- Rasm yuklash qoidasi ---------------------------------------------
    # Yangi rasm faqat ikki holatda yuklanadi:
    #   1) foydalanuvchida hali rasm yo'q
    #   2) admin oldingi rasmni bekor qilgan
    # "Kutilmoqda" yoki "Tasdiqlangan" rasmni almashtirib (yoki o'chirib) bo'lmaydi.

    @property
    def can_upload_image(self):
        """View/serializer'da yuklash formasini ko'rsatish-ko'rsatmaslik uchun."""
        return not self.image or self.image_status == self.ImageStatus.REJECTED

    def _saved_image_state(self):
        """Bazadagi (hali o'zgartirilmagan) rasm yo'li va holati."""
        if self._state.adding:
            return '', None
        row = type(self).objects.filter(pk=self.pk).values_list('image', 'image_status').first()
        return row or ('', None)

    def _image_changed(self, saved_image):
        return (self.image.name or '') != (saved_image or '')

    def clean(self):
        super().clean()
        errors = {}

        saved_image, saved_status = self._saved_image_state()
        if (
            self._image_changed(saved_image)
            and saved_image
            and saved_status != self.ImageStatus.REJECTED
        ):
            if saved_status == self.ImageStatus.APPROVED:
                errors['image'] = "Rasmingiz tasdiqlangan, uni o'zgartirib bo'lmaydi."
            else:
                errors['image'] = (
                    "Rasmingiz admin tomonidan ko'rib chiqilmoqda. "
                    "Yangi rasmni faqat admin bekor qilgandan keyin yuklash mumkin."
                )

        if self.image_status == self.ImageStatus.REJECTED and not self.rejection_reason.strip():
            errors['rejection_reason'] = "Rasm bekor qilinganda sababini yozish majburiy."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields')
        if update_fields is None or 'image' in update_fields:
            saved_image, _ = self._saved_image_state()
            # Bekor qilingan rasm o'rniga yangisi yuklandi -> qayta ko'rib chiqishga
            if (
                self.image
                and self._image_changed(saved_image)
                and self.image_status == self.ImageStatus.REJECTED
            ):
                self.image_status = self.ImageStatus.PENDING

        # Holat "Bekor qilingan" bo'lmasa, eski sabab foydalanuvchiga chiqib qolmasin
        if self.image_status != self.ImageStatus.REJECTED:
            self.rejection_reason = ''
        super().save(*args, **kwargs)
