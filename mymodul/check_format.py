import os
import imghdr


def is_supported_image(file_path):
    # Перевірка, чи є файл зображенням з підтримуваним форматом
    supported_formats = ['jpeg', 'png', 'gif', 'bmp']
    image_format = imghdr.what(file_path)
    return image_format in supported_formats
