from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from cloudinary.models import CloudinaryField
from cloudinary.uploader import upload
from cloudinary_storage.storage import MediaCloudinaryStorage
import qrcode
from io import BytesIO
from plans.models import Plan


class Memorial(models.Model):
    """Core model representing a memorial profile."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    banner_type = models.CharField(
        max_length=10,
        choices=[('image', 'Image'), ('color', 'Color')],
        default='color'
    )
    banner_value = models.CharField(max_length=255, blank=True, default='#f7e8c9')
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    date_of_death = models.DateField(blank=True, null=True)
    quote = models.TextField(blank=True, null=True)
    biography = models.TextField(blank=True, null=True, verbose_name="Memorial Biography")
    created_at = models.DateTimeField(default=timezone.now)

    # Cloudinary references
    profile_public_id = models.CharField(max_length=300, blank=True, null=True)
    audio_public_id = models.CharField(max_length=300, blank=True, null=True)
    qr_code_public_id = models.CharField(max_length=300, blank=True, null=True)

    # Profile picture
    def profile_picture_upload_path(instance, filename):
        return f"memorials/{instance.id}/profile_pictures/{filename}"

    profile_picture = models.ImageField(
        upload_to=profile_picture_upload_path,
        blank=True,
        null=True,
        storage=MediaCloudinaryStorage()
    )

    # Audio file
    def audio_file_upload_path(instance, filename):
        return f"memorials/{instance.id}/audio/{filename}"

    audio_file = CloudinaryField(
        resource_type='raw',
        folder=audio_file_upload_path,
        blank=True,
        null=True
    )

    # QR Code
    def qr_code_upload_path(instance, filename):
        return f"memorials/{instance.id}/qr_codes/{filename}"

    qr_code = models.ImageField(
        upload_to=qr_code_upload_path,
        blank=True,
        null=True,
        storage=MediaCloudinaryStorage()
    )

    # Subscription fields
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        """Custom save to handle QR code generation."""
        if not self.id:
            super().save(*args, **kwargs)

        if not self.qr_code:
            self.generate_qr_code()

        super().save(*args, **kwargs)

    def generate_qr_code(self):
        """Generates and uploads QR code to Cloudinary."""
        url = f"http://localhost:8000/memorials/{self.id}/"
        qr_img = qrcode.make(url)

        buffer = BytesIO()
        qr_img.save(buffer, format="PNG")
        buffer.seek(0)

        try:
            upload_result = upload(
                buffer,
                folder=f"memorials/{self.id}/qr_codes",
                public_id=f"qr_code_{self.id}",
                overwrite=True,
                resource_type="image",
                format="png"
            )
            self.qr_code_public_id = upload_result['public_id']
            self.qr_code = None
        except Exception as e:
            print(f"Failed to upload QR code: {str(e)}")
            raise

    def get_qr_code_url(self):
        """Returns full Cloudinary URL for the QR code."""
        if self.qr_code_public_id:
            return f"https://res.cloudinary.com/neverforgotten/image/upload/{self.qr_code_public_id}.png"
        return None

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Tribute(models.Model):
    """Model for memorial tributes/messages."""
    memorial = models.ForeignKey(Memorial, related_name='tributes', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    author_name = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Tribute by {self.author_name} for {self.memorial}"


class GalleryImage(models.Model):
    """Model for memorial gallery images."""
    memorial = models.ForeignKey(Memorial, on_delete=models.CASCADE, related_name='gallery')
    image = CloudinaryField('image')
    caption = models.CharField(max_length=255, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Image for {self.memorial}"