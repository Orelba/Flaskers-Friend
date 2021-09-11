from flask import Blueprint, render_template
from ..models import Announcements

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(404)
def error_404(error):
    anns = Announcements.query.order_by(Announcements.date_posted.desc())
    return render_template('errors/404.html', anns=anns), 404  # In flask you can return a status code as a second value


@errors.app_errorhandler(403)
def error_403(error):
    anns = Announcements.query.order_by(Announcements.date_posted.desc())
    return render_template('errors/403.html', anns=anns), 403


@errors.app_errorhandler(500)
def error_500(error):
    anns = Announcements.query.order_by(Announcements.date_posted.desc())
    return render_template('errors/500.html', anns=anns), 500
