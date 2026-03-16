from abc import ABC
from typing import Generator
from pathlib import Path
import random
import base64
import os
import sys
class AvatarImage(ABC):
    def convert_image_to_binary(cls, image_path: Path) -> bytes:
        """
        Вытаскивание бинарных данных из изображения.
        """
        binary_data: bytes = bytes()
        with open(image_path.absolute(), 'rb') as image:
            binary_data = image.read()
        return binary_data
    
    def sync_avatars() -> list[Path]:
        """
        Синхронизация аватарок с фактическими аватарками в директории os.environ['AVATARS_DIR']
        """
        avatars_list = [avatar for avatar in Path(f'{os.environ['AVATARS_DIR']}').iterdir() ]
        return avatars_list

    def get_random_image_path(cls):
        avatars: list[Path] =  AvatarImage.sync_avatars() # синхронизируем аватарки из директории аватарок
        random.seed(int.from_bytes(os.urandom(16)))
        random_avatar: Path = random.choice(avatars)
        return random_avatar

