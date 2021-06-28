import os, secrets
from flask import current_app
from PIL import Image

def save_file_licenese(file):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(file.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/licenses', picture_fn)
    file.save(picture_path)
    return picture_fn

def save_file_sign(file):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(file.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/signs', picture_fn)
    i = Image.open(file)
    i.save(picture_path)
    file.save(picture_path)
    return picture_fn