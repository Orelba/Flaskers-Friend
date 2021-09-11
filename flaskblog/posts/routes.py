from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from flask_login import current_user, login_required
from .. import db  # Comes from __init__.py
from ..models import Post, Announcements
from ..posts.forms import PostForm

posts = Blueprint('posts', __name__)


@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    anns = Announcements.query.order_by(Announcements.date_posted.desc())
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)  # Defining the post
        db.session.add(post)  # Adding the post to the database
        db.session.commit()  # Committing changes to the database (Necessary)
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post', form=form, anns=anns, legend='New Post')


@posts.route("/post/<int:post_id>")
def post(post_id):
    anns = Announcements.query.order_by(Announcements.date_posted.desc())
    post = Post.query.get_or_404(post_id)  # Returns data from the database if it exists, if not it returns 404.
    return render_template('post.html', title=post.title, post=post, anns=anns)


@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    anns = Announcements.query.order_by(Announcements.date_posted.desc())
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        if current_user.admin is False:
            abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        if current_user.admin and post.author != current_user:
            flash(f"{post.author.username}'s post has been updated!", 'success')
        else:
            flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, anns=anns, legend='Update Post')


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    post_likes = post.likes.all()
    post_dislikes = post.dislikes.all()
    post_saves = post.saves.all()
    if post.author != current_user:
        if current_user.admin is False:
            abort(403)

    for like in post_likes:
        db.session.delete(like)
    for dislike in post_dislikes:
        db.session.delete(dislike)
    for save in post_saves:
        db.session.delete(save)
    db.session.delete(post)
    db.session.commit()

    if current_user.admin and post.author != current_user:
        flash(f"{post.author.username}'s post has been deleted!", 'success')
    else:
        flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))


@posts.route("/post_action/<int:post_id>/<action>")  # ADDED
@login_required
def post_action(post_id, action):
    post = Post.query.filter_by(id=post_id).first_or_404()
    if action == 'like':
        current_user.like_post(post)
        db.session.commit()
    if action == 'dislike':
        current_user.dislike_post(post)
        db.session.commit()
    if action == 'save':
        current_user.save_unsave_post(post)
        db.session.commit()
    if action == 'unsave':
        current_user.save_unsave_post(post)
        db.session.commit()
    return redirect(request.referrer)
