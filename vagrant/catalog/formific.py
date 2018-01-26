from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, jsonify, abort
    )
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from models import Base, Medium, ArtItem, User
from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import json
import httplib2
import requests
from flask import make_response
from functools import wraps


app = Flask(__name__)

engine = create_engine('sqlite:///formific.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Formific Item Catalog"


def login_required(func):
    """ Check if user is logged in.

    This decorator verfies whether a user is logged in before
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
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        print kwargs
        item = session.query(ArtItem).filter_by(id=kwargs['item_id']).one_or_none()
        if not item:
            return abort(404)
        else:
            return func(*args, **kwargs)
    return wrapper    


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read()
        )['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (  # noqa
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
      Due to the formatting for the result from the server token exchange we
      have to split the token first on commas and select the first index which
      gives us the key : value for the server access token then we split it
      on colons to pull out the actual token value and replace the remaining
      quotes with nothing so that it can be used directly in the graph
      api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '''
        " style = "width: 300px; height: 300px;border-radius: 150px;
            -webkit-border-radius: 150px;-moz-border-radius: 150px;">
            '''

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)  # noqa
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(
            'client_secrets.json', scope=''
            )
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)  # noqa
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')

    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = (
            make_response(json.dumps(
                'Current user is already connected.'
                ), 200)
        )
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    print "Username is:"
    print login_session['username']

    # check if user exists, if not, create a new user in the database
    userId = getUserID(login_session['email'])
    if not userId:
        userId = createUser(login_session)
    login_session['user_id'] = userId
    print "The User ID is: {}".format(userId)

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += (
        ' " style = "width: 300px; height: 300px;border-radius: 150px; '
        '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
        )
    print "done!"
    return output


# Disconnect
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = (
            make_response(json.dumps(
                'Current user not connected.'), 401)
        )
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s' % access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        print "result is not 200"
        response = (
            make_response(json.dumps(
                    'Failed to revoke token for given user.', 400)
            ))
        response.headers['Content-Type'] = 'application/json'
        return response


# User Helper Functions
def createUser(login_session):
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture']
    )
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# JSON APIs to view item information
@app.route('/formific/medium/<medium_name>/JSON')
def showMediumItems(medium_name):
    medium = session.query(Medium).filter_by(name=medium_name).one()
    items = session.query(ArtItem).filter_by(medium_id=medium.id).all()
    return jsonify(mediumItems=[i.serialize for i in items])


@app.route('/formific/items/JSON')
def showAllItems():
    items = session.query(ArtItem).all()
    return jsonify(items=[i.serialize for i in items])


# Show all medium categories
@app.route('/', methods=['GET'])
@app.route('/formific', methods=['GET'])
def showForms():
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
@app.route('/formific/medium/<medium_name>/')
@app.route('/formific/medium/<medium_name>/item')
@category_exists
def showItems(medium_name):
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


@app.route('/formific/medium/<medium_name>/item/<int:item_id>')
@category_exists
@item_exists
def showItem(medium_name, item_id):
    formList = session.query(Medium).all()
    item = session.query(ArtItem).filter_by(id=item_id).one()
    if ('username' not in login_session or
            item.user_id != login_session['user_id']):
        return render_template(
            'public-item.html',
            item=item,
            media=formList,
            userinfo=login_session
        )
    else:
        return render_template(
            'item.html',
            item=item,
            media=formList,
            userinfo=login_session
        )


@app.route('/formific/item/new', methods=['GET', 'POST'])
@login_required
def newItem():
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


@app.route('/formific/item/<int:item_id>/edit', methods=['GET', 'POST'])
@item_exists
@login_required
@item_modification_authentication
def editItem(item_id):
    formList = session.query(Medium).all()
    editedItem = session.query(ArtItem).filter_by(id=item_id).one()
    # if editedItem.user_id != login_session['user_id']:
    #     flash('You are not authorized to edit this item. You must be the creator of an item to edit or delete it.')
    #     return redirect(url_for('showItem', medium_name=editedItem.medium.name, item_id=editedItem.id))
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


@app.route('/formific/item/<int:item_id>/delete', methods=['GET', 'POST'])
@item_exists
@login_required
@item_modification_authentication
def deleteItem(item_id):
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


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            print "Disconnecting from google login"
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showForms'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showForms'))

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
