from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from cloudinary.uploader import destroy
from cloudinary.api import resources, delete_resources, delete_folder
from urllib.parse import urlparse
import re
import logging
from time import sleep
from memorial.models import Memorial

logger = logging.getLogger(__name__)


def get_public_id_from_url(url):
    """Extracts Cloudinary public_id from URL, handles various formats."""
    parsed = urlparse(url)
    path = parsed.path
    match = re.search(r'/upload/(?:v\d+/)?(?P<public_id>.+)', path)
    return match.group('public_id') if match else None


@receiver(post_delete, sender=Memorial)
def delete_memorial_cloudinary_data(sender, instance, **kwargs):
    """Handles cleanup of all Cloudinary resources when a memorial is deleted."""
    logger.info(f"Starting deletion of memorial ID {instance.id}")

    # Delete individual files first
    for field in ['qr_code', 'profile_picture', 'audio_file']:
        file = getattr(instance, field)
        if file:
            logger.info(f"Processing field: {field}")
            file_url = getattr(file, 'url', str(file))
            public_id = get_public_id_from_url(file_url)

            if public_id:
                try:
                    destroy(public_id)
                    logger.info(f"Deleted {field}")
                except Exception as e:
                    logger.error(f"Error deleting {field}: {e}")

    # Delete all resources in memorial folder
    folder_path = f"memorials/{instance.id}"
    try:
        logger.info(f"Cleaning folder: {folder_path}")
        
        # Get all resources (paginated)
        all_resources = []
        next_cursor = None
        while True:
            response = resources(
                type="upload",
                prefix=f"{folder_path}/",
                max_results=500,
                next_cursor=next_cursor
            )
            all_resources.extend(response['resources'])
            next_cursor = response.get('next_cursor')
            if not next_cursor:
                break

        if all_resources:
            public_ids = [res['public_id'] for res in all_resources]
            logger.info(f"Found {len(public_ids)} resources to delete")
            
            # Delete in batches
            for i in range(0, len(public_ids), 100):
                batch = public_ids[i:i+100]
                try:
                    delete_resources(batch)
                    logger.info(f"Deleted batch {i//100 + 1}")
                    sleep(0.5)  # Rate limiting
                except Exception as e:
                    logger.error(f"Error deleting batch: {e}")

        # Attempt folder deletion
        try:
            delete_folder(folder_path)
            logger.info(f"Folder deletion initiated")
        except Exception as e:
            logger.warning(f"Folder may not delete immediately: {e}")

    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
    finally:
        logger.info(f"Completed cleanup for memorial {instance.id}")


@receiver(pre_save, sender=Memorial)
def delete_old_files_on_update(sender, instance, **kwargs):
    """Deletes old Cloudinary files when memorial files are updated."""
    if not instance.pk:
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    for field in ['profile_picture', 'audio_file']:
        old_file = getattr(old_instance, field)
        new_file = getattr(instance, field)

        if old_file and old_file != new_file:
            logger.info(f"Updating field {field} - deleting old file")
            file_url = getattr(old_file, 'url', str(old_file))
            public_id = get_public_id_from_url(file_url)

            if public_id:
                try:
                    destroy(public_id)
                    logger.info(f"Deleted old {field}")
                except Exception as e:
                    logger.error(f"Error deleting old {field}: {e}")