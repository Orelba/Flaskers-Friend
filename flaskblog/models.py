from datetime import datetime
import pytz
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from . import db, login_manager
from flask_login import UserMixin


def time_now():
    return datetime.now(tz=pytz.timezone('Israel'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    admin = db.Column(db.Integer, nullable=False, default=0)  # Self Added

    posts = db.relationship('Post', backref='author', lazy=True)  # Here we refer the post class
    liked = db.relationship('PostLike', foreign_keys='PostLike.user_id', backref='user', lazy='dynamic')
    disliked = db.relationship('PostDislike', foreign_keys='PostDislike.user_id', backref='user', lazy='dynamic')
    saved = db.relationship('PostSave', foreign_keys='PostSave.user_id', backref='user', lazy='dynamic')

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)  # Setting an initial token for verification
        return s.dumps({'user_id': self.id}).decode('utf-8')  # Returning the initial token for the user id

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']  # Checking if the token is valid (doesn't raise an error)
        except:
            return None  # If token isn't valid (raises an exception)
        return User.query.get(user_id)  # If token is valid we are returning the user id from the database

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}', '{self.admin}')"

    def like_post(self, post):
        if self.has_liked_post(post):
            PostLike.query.filter_by(user_id=self.id, post_id=post.id).delete()
        else:
            if not self.has_disliked_post(post):
                like = PostLike(user_id=self.id, post_id=post.id)
                db.session.add(like)
            else:
                PostDislike.query.filter_by(user_id=self.id, post_id=post.id).delete()
                like = PostLike(user_id=self.id, post_id=post.id)
                db.session.add(like)

    def dislike_post(self, post):
        if self.has_disliked_post(post):
            PostDislike.query.filter_by(user_id=self.id, post_id=post.id).delete()
        else:
            if not self.has_liked_post(post):
                dislike = PostDislike(user_id=self.id, post_id=post.id)
                db.session.add(dislike)
            else:
                PostLike.query.filter_by(user_id=self.id, post_id=post.id).delete()
                dislike = PostDislike(user_id=self.id, post_id=post.id)
                db.session.add(dislike)

    def save_unsave_post(self, post):
        if not self.has_saved_post(post):
            save = PostSave(user_id=self.id, post_id=post.id)
            db.session.add(save)
        else:
            PostSave.query.filter_by(user_id=self.id, post_id=post.id).delete()

    def has_liked_post(self, post):
        return PostLike.query.filter(PostLike.user_id == self.id, PostLike.post_id == post.id).count() > 0

    def has_disliked_post(self, post):
        return PostDislike.query.filter(PostDislike.user_id == self.id, PostDislike.post_id == post.id).count() > 0

    def has_saved_post(self, post):
        return PostSave.query.filter(PostSave.user_id == self.id, PostSave.post_id == post.id).count() > 0


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=time_now)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # ForeignKey refers User table key
    likes = db.relationship('PostLike', backref='post', lazy='dynamic')
    dislikes = db.relationship('PostDislike', backref='post', lazy='dynamic')
    saves = db.relationship('PostSave', backref='post', lazy='dynamic')

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


class PostLike(db.Model):
    __tablename__ = 'post_like'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))


class PostDislike(db.Model):
    __tablename__ = 'post_dislike'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))


class PostSave(db.Model):
    __tablename__ = 'post_save'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    date_saved = db.Column(db.DateTime, nullable=False, default=time_now)


class Announcements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=time_now, onupdate=time_now)
