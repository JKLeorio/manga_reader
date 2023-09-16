from django.core.exceptions import ValidationError


def validate_archive_extension(archive):
    if archive.name.split('.')[-1] != 'zip':
        raise ValidationError('the file must be a zip archive')


def validate_image(image):
    errors = []
    image_formats = ['jpeg', 'png', 'jpg']
    added_images = []

    not_image = image.filename.split('.')[-1] not in image_formats
    name_is_number = image.filename.split('.')[0].isnumeric()

    if image.is_dir() or not_image:
        errors.append('archive must contain only images files')

    elif not name_is_number:
        errors.append('file name must contain only numbers')

    if image.filename in added_images:
        errors.append('file names must be unique')
        return errors

    added_images.append(image.filename)

    return errors