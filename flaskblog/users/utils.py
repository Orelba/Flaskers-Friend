import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_login import current_user
from flask_mail import Message
from .. import mail


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    old_picture = current_user.image_file  # Self added

    output_size = (250, 250)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    if old_picture != 'default.jpg':
        os.remove(f'{current_app.root_path}/static/profile_pics/{old_picture}')
    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    email = os.environ.get('EMAIL_USER')
    msg = Message('Password Reset Request', sender=email, recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)
