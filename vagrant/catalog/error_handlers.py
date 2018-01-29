import flask
from flask import render_template
from database import session
from models.user import User
from models.medium import Medium
from models.artitem import ArtItem

blueprint = flask.Blueprint('error_handlers', __name__)

@blueprint.app_errorhandler(404)
def page_not_found(e):
    """Returns a 404 page when content is not found"""
    media = session.query(Medium).all()
    return render_template('404.html', media=media), 404


@blueprint.app_errorhandler(401)
def unauthorized(e):
    """Returns a 401 page if the user credentials fail"""
    media = session.query(Medium).all()
    return render_template('401.html', media=media), 401


@blueprint.app_errorhandler(500)
def server_error(e):
    """Returns a 500 page when the server fails"""
    return render_template('500.html'), 500