import os

import aiohttp
import urllib.parse

from newsbot import settings


class ImgurSession(aiohttp.ClientSession):
    def __init__(self, *args, **kwargs):
        imgur_client_id = kwargs.pop('imgur_client_id', settings.IMGUR_CLIENT_ID)
        kwargs.setdefault('headers', dict())
        kwargs['headers'].setdefault('Authorization', 'Client-ID ' + imgur_client_id)
        super(ImgurSession, self).__init__(*args, **kwargs)

    async def get_imgur_images(self, imgur_url):
        split_result = urllib.parse.urlsplit(imgur_url)
        if split_result.path.startswith('/a/') or split_result.path.startswith('/gallery/'):
            album_id = split_result.path.split('/')[-1]
            async for image in self.get_imgur_album_images(album_id):
                yield image
        else:
            image_id = os.path.splitext(split_result.path[1:])[0]
            yield self.get_imgur_image(image_id)

    async def get_imgur_image(self, image_id):
        async with self.get('https://api.imgur.com/3/image/' + image_id) as response:
            image = await response.json()
        if not image.get('success', False):
            return
        return image.get('data', None)

    async def get_imgur_album_images(self, album_id):
        async with self.get('https://api.imgur.com/3/album/' + album_id) as response:
            album = await response.json()
        if not album.get('success', False):
            return
        for image in album.get('data', {}).get('images', []):
            yield image