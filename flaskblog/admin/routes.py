import os
from flask import render_template, url_for, flash, redirect, request, current_app, Blueprint
from flask_login import current_user
from .. import db, bcrypt
from ..models import User, Post, Announcements
from ..admin.forms import ManageUserForm, AddUserForm, AddAnnouncementForm
from ..admin.utils import admin_auth
from ..admin.utils import save_user_picture, save_add_user_picture

admin = Blueprint('admin', __name__)

users_per_page = 8


@admin.route("/panel")
@admin_auth
def admin_panel():
    page = request.args.get('page', 1, type=int)
    users = User.query.filter_by(id=User.id).paginate(page=page, per_page=users_per_page)
    return render_template('admin/admin_panel.html', title='Admin Panel',
                           users=users, per_page=users_per_page, Post=Post())


@admin.route("/panel/")
@admin_auth
def admin_panel_redirect():
    return redirect(url_for('admin.admin_panel'))


@admin.route("/panel/manage_user/<int:user_id>", methods=['GET', 'POST'])
@admin_auth
def manage_user(user_id):
    page = request.args.get('page', 1, type=int)
    user = User.query.get_or_404(user_id)
    form = ManageUserForm(user)
    users = User.query.filter_by(id=User.id).paginate(page=page, per_page=users_per_page)

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_user_picture(user, form.picture.data)
            user.image_file = picture_file
        user.username = form.username.data
        user.email = form.email.data
        if form.admin.data == 'Admin':
            user.admin = True
        elif form.admin.data == 'User' and user != current_user:
            if user.id != 1:
                user.admin = False
            else:
                flash("You cannot change the founder's status!", 'danger')
                return redirect(url_for('admin.admin_panel', page=page))
        else:
            flash('You cannot change your own status!', 'danger')
            return redirect(url_for('admin.admin_panel', page=page))
        db.session.commit()
        flash('This account has been updated!', 'success')
        return redirect(url_for('admin.admin_panel', page=page))

    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        if user.admin:
            form.admin.data = 'Admin'
        else:
            form.admin.data = 'User'

    image_file = url_for('static', filename=f'profile_pics/{user.image_file}')
    return render_template('admin/manage_user.html', title='Admin Panel', user=user, users=users,
                           image_file=image_file, per_page=users_per_page, form=form, Post=Post())


@admin.route("/panel/manage_user/<int:user_id>/delete", methods=['POST'])
@admin_auth
def manage_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    user_posts = Post.query.filter_by(user_id=user_id).all()  # user_id posts
    all_posts = Post.query.all()
    if user == current_user or user.id == 1:
        flash(f'You cannot delete your own user!', 'danger')
        return redirect(url_for('admin.admin_panel'))

    if user.image_file != 'default.jpg':
        os.remove(f'{current_app.root_path}/static/profile_pics/{user.image_file}')

    # All Posts > user_id likes, dislikes, saves in all posts (only by user_id)
    for post in all_posts:
        likes = post.likes.filter_by(user_id=user_id).all()
        dislikes = post.dislikes.filter_by(user_id=user_id).all()
        saves = post.saves.filter_by(user_id=user_id).all()
        for like in likes:
            db.session.delete(like)
        for dislike in dislikes:
            db.session.delete(dislike)
        for save in saves:
            db.session.delete(save)
    # user_id Posts > All likes, dislikes, saves in user to delete posts (by everyone including user_id)
    for post in user_posts:
        likes = post.likes.all()
        dislikes = post.dislikes.all()
        saves = post.saves.all()
        for like in likes:
            db.session.delete(like)
        for dislike in dislikes:
            db.session.delete(dislike)
        for save in saves:
            db.session.delete(save)
        db.session.delete(post)

    db.session.delete(user)
    db.session.commit()

    flash(f'The user {user.username} has been deleted!', 'success')
    return redirect(url_for('admin.admin_panel'))


@admin.route("/panel/add_user", methods=['GET', 'POST'])
@admin_auth
def add_user():
    form = AddUserForm()
    page = request.args.get('page', 1, type=int)
    users = User.query.filter_by(id=User.id).paginate(page=page, per_page=users_per_page)

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        if form.admin.data == 'Admin':  # Form gets 'Admin'/'User' but database needs an Integer/Boolean
            form.admin.data = True
        elif form.admin.data == 'User':
            form.admin.data = False
        try:
            picture_file = save_add_user_picture(form.picture.data)
            user = User(username=form.username.data, email=form.email.data, password=hashed_password,
                        admin=form.admin.data, image_file=picture_file)
        except AttributeError:
            user = User(username=form.username.data, email=form.email.data, password=hashed_password,
                        admin=form.admin.data)
        db.session.add(user)
        db.session.commit()
        flash(f'A new account has been created for "{form.username.data}"!', 'success')
        return redirect(url_for('admin.admin_panel', page=page))
    return render_template('admin/add_user.html', title='Admin Panel',
                           form=form, users=users, per_page=users_per_page, Post=Post())


@admin.route("/announcements")
@admin_auth
def announcements():
    anns = Announcements.query.order_by(Announcements.date_posted.desc())
    return render_template('admin/announcements.html', title='Manage Announcements', anns=anns)


@admin.route("/announcements/<int:ann_id>/edit", methods=['GET', 'POST'])
@admin_auth
def edit_ann(ann_id):
    anns = Announcements.query.order_by(Announcements.date_posted.desc())
    ann = Announcements.query.get_or_404(ann_id)
    form = AddAnnouncementForm()
    if form.validate_on_submit():
        ann.content = form.content.data
        db.session.commit()
        flash('The announcement has been updated!', 'success')
        return redirect(url_for('admin.announcements'))
    elif request.method == 'GET':
        form.content.data = ann.content
    return render_template('admin/add_ann.html', title='Manage Announcements',
                           anns=anns, form=form, legend='Edit Announcement')


@admin.route("/announcements/add", methods=['GET', 'POST'])
@admin_auth
def add_ann():
    anns = Announcements.query.order_by(Announcements.date_posted.desc())
    form = AddAnnouncementForm()
    if form.validate_on_submit():
        announcement = Announcements(content=form.content.data)
        db.session.add(announcement)
        db.session.commit()
        flash('Your announcement has been created!', 'success')
        return redirect(url_for('admin.announcements'))
    return render_template('admin/add_ann.html', title='Manage Announcements',
                           anns=anns, form=form, legend='Add Announcement')


@admin.route("/announcements/<int:ann_id>/delete", methods=['GET', 'POST'])
@admin_auth
def delete_ann(ann_id):
    ann = Announcements.query.get_or_404(ann_id)
    db.session.delete(ann)
    db.session.commit()
    flash('The announcement has been deleted!', 'danger')
    return redirect(url_for('admin.announcements'))
