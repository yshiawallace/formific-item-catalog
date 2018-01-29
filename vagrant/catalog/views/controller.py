from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, jsonify, abort, Blueprint
    )
from sqlalchemy import asc
from database import init_db
from database import session
from models.user import User
from models.medium import Medium
from models.artitem import ArtItem
from flask import session as login_session
from flask import make_response
from functools import wraps


views = Blueprint('views', __name__, template_folder='templates/')


def login_required(func):
    """ Check if user is logged in.

    This is a decorator that verfies whether a user is logged in before
    allowing access to the requested resource. If they are
    not logged in, they are redirected to the login page.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        else:
            return func(*args, **kwargs)
    return wrapper


def item_modification_authentication(func):
    """ Check if user is owner of an item.

    This is a decorator that checks whether a user is the owner 
    of a specific item before they are allowed to edit or delete it.
    If they are not the owner, they are flashed a message.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        item_id = kwargs['item_id']
        item = session.query(ArtItem).filter_by(id=item_id).one_or_none()
        if item.user_id != login_session['user_id']:
            flash('You are not authorized to edit this item. You must be the creator of an item to edit or delete it.')
            return redirect(url_for('showItem', medium_name=item.medium.name, item_id=item.id))
        else:
            return func(*args, **kwargs)
    return wrapper


def category_exists(func):
    """ Check if a category exists.

    This is a decorator that checks whether a category exists in
    the database. If the category does not exist, a 404 error
    is returned.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        category = session.query(Medium).filter_by(name=kwargs['medium_name']).one_or_none()
        if not category:
            return abort(404)
        else:
            return func(*args, **kwargs)
    return wrapper


def item_exists(func):
    """ Check if a item exists.

    This is a decorator that checks whether an item exists in
    the database. If the category does not exist, a 404 error
    is returned.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        item = session.query(ArtItem).filter_by(id=kwargs['item_id']).one_or_none()
        if not item:
            return abort(404)
        else:
            return func(*args, **kwargs)
    return wrapper


# JSON APIs to view item information
@views.route('/formific/medium/<medium_name>/JSON')
@category_exists
def showMediumItems(medium_name):
    """JSON endpoint to display all items in a specific category"""
    medium = session.query(Medium).filter_by(name=medium_name).one()
    items = session.query(ArtItem).filter_by(medium_id=medium.id).all()
    return jsonify(mediumItems=[i.serialize for i in items])


@views.route('/formific/items/JSON')
def showAllItems():
    """JSON endpoint to display all items in the database"""
    items = session.query(ArtItem).all()
    return jsonify(items=[i.serialize for i in items])


# Show all medium categories
@views.route('/', methods=['GET'])
@views.route('/formific', methods=['GET'])
def showForms():
    """Renders the main page populated with all items and categories"""
    formList = session.query(Medium).all()
    recentItems = (
            session.query(ArtItem).order_by(ArtItem.id.desc()).limit(12).all()
        )
    return render_template(
        'formific.html',
        media=formList,
        items=recentItems,
        userinfo=login_session
    )   


# Show all items in a category
@views.route('/formific/medium/<medium_name>/')
@views.route('/formific/medium/<medium_name>/item')
@category_exists
def showItems(medium_name):
    """Renders a page that displays all items within a specific category"""
    formList = session.query(Medium).all()
    medium = session.query(Medium).filter_by(name=medium_name).first()
    items = session.query(ArtItem).filter_by(medium_id=medium.id).all()
    return render_template(
        'items.html',
        medium=medium,
        items=items,
        media=formList,
        userinfo=login_session
    )


@views.route('/formific/medium/<medium_name>/item/<int:item_id>')
@category_exists
@item_exists
def showItem(medium_name, item_id):
    """Renders a page that displays a specific item in a category"""
    formList = session.query(Medium).all()
    item = session.query(ArtItem).filter_by(id=item_id).one()
    return render_template(
        'item.html',
        item=item,
        media=formList,
        userinfo=login_session
    )


@views.route('/formific/item/new', methods=['GET', 'POST'])
@login_required
def newItem():
    """Render a page that displays an HTML form to create a new item

    Renders a page with an HTML form. When the form is submitted a
    new item is created in the database with the form values submitted.
    """
    formList = session.query(Medium).all()
    if request.method == 'POST':
        newItem = ArtItem(
            name=request.form['name'],
            description=request.form['description'],
            material=request.form['material'],
            image_url=request.form['image_url'],
            video_url=request.form['video_url'],
            year=request.form['year'],
            medium_id=request.form['medium'],
            user_id=login_session['user_id']
        )
        session.add(newItem)
        session.commit()
        return redirect(url_for('showForms'))
    else:
        return render_template(
            'new-item.html',
            media=formList,
            userinfo=login_session
        )


@views.route('/formific/item/<int:item_id>/edit', methods=['GET', 'POST'])
@item_exists
@login_required
@item_modification_authentication
def editItem(item_id):
    """Render a page that displays an HTML form to edit an item

    Renders a page with an HTML form that allows the owner of the
    item to edit and update the item details.
    """
    formList = session.query(Medium).all()
    editedItem = session.query(ArtItem).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['material']:
            editedItem.material = request.form['material']
        if request.form['image_url']:
            editItem.image_url = request.form['image_url']
        if request.form['video_url']:
            editItem.video_url = request.form['video_url']
        if request.form['year']:
            editedItem.year = request.form['year']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('showForms'))
    else:
        return render_template(
            'edit-item.html',
            item=editedItem,
            media=formList,
            userinfo=login_session
        )


@views.route('/formific/item/<int:item_id>/delete', methods=['GET', 'POST'])
@item_exists
@login_required
@item_modification_authentication
def deleteItem(item_id):
    """Render a page that displays an HTML input to delete an item

    Renders a page with an HTML input that allows the owner of the
    item to delete it.
    """
    formList = session.query(Medium).all()
    item = session.query(ArtItem).filter_by(id=item_id).one()
    if item.user_id != login_session['user_id']:
        flash('You are not authorized to edit this item. You must be the creator of an item to edit or delete it.')
        return redirect(url_for('showItem', medium_name=item.medium.name, item_id=item.id))    
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        return redirect(url_for('showForms'))
    else:
        return render_template(
            'delete-item.html',
            item=item,
            media=formList,
            userinfo=login_session
        )
