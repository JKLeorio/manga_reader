import requests
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def get_profile_img(backend, user, response, *args, **kwargs):
    if user is None:
        return None

    if backend.name == 'google-oauth2':
        image_url = response.get('picture')
        image_response = requests.get(image_url)
        image_name = f"{image_url.split('/')[-1]}.{image_response.headers['content-type'].split('/')[-1]}"
        image_path = default_storage.save(image_name,ContentFile(image_response.content))
        user.image = image_path
        user.save()