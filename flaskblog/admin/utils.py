import os
import secrets
from functools import wraps
from PIL import Image
from flask import abort, current_app
from flask_login import current_user, login_required


def admin_auth(func):
    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        if current_user.admin:
            return func(*args, **kwargs)
        return abort(403)
    return wrapper


def save_user_picture(user, form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    old_picture = user.image_file

    output_size = (250, 250)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    if old_picture != 'default.jpg':
        os.remove(f'{current_app.root_path}/static/profile_pics/{old_picture}')
    return picture_fn


def save_add_user_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    output_size = (250, 250)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn
