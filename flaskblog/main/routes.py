from flask import render_template, request, Blueprint
from ..models import Post, Announcements

main = Blueprint('main', __name__)


@main.route("/")  # The root page of our website (Homepage)
@main.route("/home")  # Giving two routes for the same function
def home():
    anns = Announcements.query.order_by(Announcements.date_posted.desc())
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts, anns=anns)


@main.route("/about")
def about():
    anns = Announcements.query.order_by(Announcements.date_posted.desc())
    return render_template('about.html', anns=anns, title='About')
