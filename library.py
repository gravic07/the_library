import random, string
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    make_response,
    session as login_session
)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from library_setup import Base, Patrons, Collections, Books
from oauth2client.client import (
    flow_from_clientsecrets,
    FlowExchangeError
    )
import httplib2
import json
import requests

app = Flask(__name__)



CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "The Library"


# Create session to talk to database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///theArchives.db'
engine = create_engine('postgres://ewcuvsjxbhzuce:lTxnaKjAsx3L5JVCsjN1NXrrnS@ec2-54-83-20-177.compute-1.amazonaws.com:5432/d6l2vgh7udooqv')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()



# User management functions
def createUser(login_session):
    ''' Takes login session as an argument and parses the data to be added to the Patrons table in the database.

    '''
    newUser = Patrons(name    = login_session['username'],
                      email   = login_session['email'],
                      picture = login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(Patrons).filter_by(email = login_session['email']).one()
    return user.id

def getUser(userID):
    ''' Takes a user ID as an argument and returns the user associated with that ID.
    '''
    user = session.query(Patrons).filter_by(id = userID).one()
    return user

def getUserID(email):
    ''' Takes an email as an argument and returns the ID of the user associated to that email address.
    '''
    try:
        user = session.query(Patrons).filter_by(email = email).one()
        return user.id
    except:
        return None





# LOGIN
@app.route('/login/')
def loginPage():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    print state
    return render_template('login.html', STATE=state)



@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['credentials']
            del login_session['gplus_id']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash('You have successfully been logged out.')
        return redirect(url_for('homePage'))
    else:
        flash('You are not currenlty logged in.')
        return redirect(url_for('homePage'))



@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        print "session doesn't match!"
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        print "Check #1"
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        print "Flow exchange error."
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    print "Check #2"
    result = json.loads(h.request(url, 'GET')[1])
    # Abort if there is an error in the access token info
    if result.get('error') is not None:
        print "There was some kind of error"
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token matches the intended user
    gplus_id = credentials.id_token['sub']
    print "Check #3"
    if result['user_id'] != gplus_id:
        print "toekn ID doesn't match google id"
        response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        print "client IDs don't match"
        response = make_response(json.dumps("Token's client ID does not match the app's client ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check is user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    print "Check #3"
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already logged in.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id
    print "Check #4"

    # Get user info
    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt':'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)
    print "Check #5"

    # Store user info to the login session
    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture']  = data['picture']
    login_session['email']    = data['email']
    print "Check #6"

    # Check if user exists and if not, add to database
    userID = getUserID(login_session['email'])
    if not userID:
        userID = createUser(login_session)
    # Add the user's ID to the login session
    login_session['user_id'] = userID
    print "Check #7"

    # 2DO - Update this output to be prettier...
    output = ''
    output += '<div class="jumbotron text-center">'
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style="width:100px; height:100px; border-radius:150px; -webkit-border-radius:150px; -moz-border-radius:150px;"> '
    output += '</div>'
    flash("You are now logged in as %s!" % login_session['username'])
    return output

@app.route('/gdisconnect')
def gdisconnect():
    credentials = login_session.get('credentials')
    # 2DO - Why is this 401?  Shouldn't it be 200?
    if credentials is None:
        response = make_response(json.dumps('The current user is not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Revoke token through an HTTP GET request
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('The user has been disconnected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response








@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    # Exchange client token for long lived server-side token
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # Strip expired tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.2/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user's picture
    url = 'https://graph.facebook.com/v2.2/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # Check if user exists and if not, add to database
    userID = getUserID(login_session['email'])
    if not userID:
        userID = createUser(login_session)
    # Add the user's ID to the login session
    login_session['user_id'] = userID

    # 2DO - Update this output to be prettier...
    output = ''
    output += '<div class="jumbotron text-center">'
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style="width:100px; height:100px; border-radius:150px; -webkit-border-radius:150px; -moz-border-radius:150px;"> '
    output += '</div>'
    flash("You are now logged in as %s!" % login_session['username'])
    return output

# Revoke current token and reset the login_session
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "You have been logged out."








# R - COLLECTIONS / HOMEPAGE
@app.route('/')
@app.route('/collections/')
def homePage():
    collections = session.query(Collections).all()
    books = session.query(Books).all()
    loggedIn = None
    if 'username' in login_session:
        loggedIn = login_session['user_id']
    return render_template('index.html', collections=collections, books=books, loggedIn=loggedIn)

# C - COLLECTIONS
@app.route('/collections/create/', methods=['GET', 'POST'])
def createCollections():
    collections = session.query(Collections).all()



    # Verify the user is logged in.  If not, redirect to login.

    # 2DO - Add value that determines if CRUD functions show on template
    if 'username' not in login_session:
        flash('Please log in before creating a collection.')
        return redirect('/login')




    if request.method == 'POST':
        collection = Collections(
            name = request.form['name'],
            # 2DO - I don't believe login_session['user_id'] has been defined at this point
            patronID = login_session['user_id']
        )
        # 2DO - Crappy way to stop SQLAlchemy from trying to add the same id value
        i = 0
        while i < 100:
            session.add(collection)
            i += 1
        session.commit()
        flash(collection.name + ' has been added.')
        return redirect(url_for('homePage'))
    else:
        return render_template('createCollections.html', collections=collections)

# U - COLLECTIONS
@app.route('/collections/<int:collectionID>/edit/', methods=['GET', 'POST'])
def editCollections(collectionID):
    collections = session.query(Collections).all()
    cToEdit = session.query(Collections).filter_by(id=collectionID).one()
    oldName = cToEdit.name
    # Verify the user is logged in.  If not, redirect to login.
    if 'username' not in login_session:
        flash('Please log in before editing a collection.')
        return redirect('/login')
    # Redirect to home page if the active user is not the creator of the collection
    if cToEdit.patronID != login_session['user_id']:
        flash('Only the creator of ' + cToEdit.name + ' may edit it.')
        return redirect('/collections')
    if request.method == 'POST':
        cToEdit.name = request.form['name']
        session.add(cToEdit)
        session.commit()
        flash(oldName + " updated to " + cToEdit.name + ".")
        return redirect(url_for('homePage'))
    else:
        return render_template('editCollections.html',
            collections=collections, cToEdit=cToEdit, oldName=oldName)

# D - COLLECTIONS
@app.route('/collections/<int:collectionID>/delete/', methods=['GET', 'POST'])
def deleteCollections(collectionID):
    collections = session.query(Collections).all()
    cToDelete = session.query(Collections).filter_by(id=collectionID).one()
    oldName = cToDelete.name
    # Verify the user is logged in.  If not, redirect to login.
    if 'username' not in login_session:
        flash('Please log in before deleting a collection.')
        return redirect('/login')
    # Redirect to home page if the active user is not the creator of the collection
    if cToDelete.patronID != login_session['user_id']:
        flash('Only the creator of ' + cToDelete.name + ' may delete it.')
        return redirect('/collections')
    if request.method == 'POST':
        session.delete(cToDelete)
        session.commit()
        flash(oldName + " has been deleted.")
        return redirect(url_for('homePage'))
    else:
        return render_template('deleteCollections.html',
            collection=collections, cToDelete=cToDelete, oldName=oldName)

@app.route('/collections.json')
def collectionsJSON():
    collections = session.query(Collections).all()
    return jsonify(Collections = [c.serialize for c in collections])

@app.route('/books.json')
@app.route('/collections/books.json')
def booksJSON():
    books = session.query(Books).all()
    return jsonify(Books = [b.serialize for b in books])








# R - BOOKS
@app.route('/collections/<int:collectionID>/books/')
def showBooksInCollection(collectionID):
    collections = session.query(Collections).all()
    collection = session.query(Collections).filter_by(id=collectionID).one()
    books      = session.query(Books).filter_by(collectionID=collectionID).all()
    loggedIn = None
    if 'username' in login_session:
        loggedIn = login_session['user_id']
    return render_template('collection.html', collections=collections, collection=collection, books=books, loggedIn=loggedIn)

# R - A BOOK
@app.route('/collections/<int:collectionID>/books/<int:bookID>/')
def showBook(collectionID, bookID):
    collections = session.query(Collections).all()
    collection  = session.query(Collections).filter_by(id=collectionID).one()
    book        = session.query(Books).filter_by(id=bookID).one()
    loggedIn = None
    if 'username' in login_session:
        loggedIn = login_session['user_id']
    return render_template('book.html', collections=collections, collection=collection, book=book, loggedIn=loggedIn)

# C - BOOKS
@app.route('/collections/<int:collectionID>/books/add/', methods=['GET', 'POST'])
def addBook(collectionID):
    collections = session.query(Collections).all()
    currentCollection = session.query(Collections).filter_by(id=collectionID).one()
    # Verify the user is logged in.  If not, redirect to login.
    if 'username' not in login_session:
        flash('Please log in before editing a collection.')
        return redirect('/login')
    # Redirect to home page if the active user is not the creator of the collection
    if currentCollection.patronID != login_session['user_id']:
        flash('Only the creator of ' + currentCollection.name + ' can add books to it.')
        return redirect('/collections')
    if request.method == 'POST':
        book = Books(
            title        = request.form['title'],
            author       = request.form['author'],
            genre        = request.form.get('genre'),
            coverImage   = request.form.get('coverImage'),
            description  = request.form.get('description'),
            collectionID = collectionID,
            # 2DO - I don't believe login_session['user_id'] has been defined at this point
            patronID     = login_session['user_id']
        )
        # 2DO - Crappy way to stop SQLAlchemy from trying to add the same id value
        i = 0
        while i < 100:
            session.add(book)
            i += 1
        session.commit()
        flash(book.title + ' has been added to ' + currentCollection.name + '.')
        return redirect(url_for('showBooksInCollection', collectionID=collectionID))
    else:
        return render_template('addBook.html',
            collections=collections, currentCollection=currentCollection)

# U - BOOKS
@app.route('/collections/<int:collectionID>/books/<int:bookID>/edit/', methods=['GET', 'POST'])
def editBook(collectionID, bookID):
    collections = session.query(Collections).all()
    currentCollection = session.query(Collections).filter_by(id=collectionID).one()
    bToEdit = session.query(Books).filter_by(id=bookID).one()
    originalTitle = bToEdit.title
    # Verify the user is logged in.  If not, redirect to login.
    if 'username' not in login_session:
        flash('Please log in before editing a book.')
        return redirect('/login')
    # Redirect to home page if the active user is not the one that added the book
    if bToEdit.patronID != login_session['user_id']:
        flash('Only the user that added ' + bToEdit.title + ' may edit it.')
        return redirect(url_for('showBooksInCollection', collectionID=collectionID))
    if request.method == 'POST':
        if request.form.get('title'):
            bToEdit.title = request.form['title']
        if request.form.get('author'):
            bToEdit.author = request.form['author']
        if request.form.get('genre'):
            bToEdit.genre = request.form['genre'],
        if request.form.get('coverImage'):
            bToEdit.coverImage = request.form['coverImage']
        if request.form.get('description'):
            bToEdit.description = request.form['description']
        session.add(bToEdit)
        session.commit()
        print str(originalTitle)
        print str(bToEdit.title)
        if originalTitle == bToEdit.title:
            flash(bToEdit.title + " has been updated.")
        else:
            flash(originalTitle + " has been updated and changed to " + bToEdit.title + ".")
        return redirect(url_for('showBooksInCollection', collectionID=collectionID))
    else:
        return render_template('editBook.html',
            collection=collections, currentCollection=currentCollection, bToEdit=bToEdit, bookID=bookID)

# D - BOOKS
@app.route('/collections/<int:collectionID>/books/<int:bookID>/delete/', methods=['GET', 'POST'])
def deleteBook(collectionID, bookID):
    collections = session.query(Collections).all()
    currentCollection = session.query(Collections).filter_by(id=collectionID).one()
    bToDelete = session.query(Books).filter_by(id=bookID).one()
    # Verify the user is logged in.  If not, redirect to login.
    if 'username' not in login_session:
        flash('Please log in before editing a book.')
        return redirect('/login')
    # Redirect to home page if the active user is not the one that added the book
    if bToDelete.patronID != login_session['user_id']:
        flash('Only the user that added ' + bToDelete.title + ' may delete it.')
        return redirect(url_for('showBooksInCollection', collectionID=collectionID))
    if request.method == 'POST':
        session.delete(bToDelete)
        session.commit()
        flash(bToDelete.title + " has been deleted from " + currentCollection.name)
        return redirect(url_for('showBooksInCollection', collectionID=collectionID))
    return render_template('deleteBook.html', collections=collections, currentCollection=currentCollection, bToDelete=bToDelete)

@app.route('/collections/<int:collectionID>/books.json')
def collectionBooksJSON(collectionID):
    # I would like to have the query join to Restaurants to display
    # the name and of the restaurant (can do id now using restaurant_id)
    books = session.query(Books).filter_by(collectionID=collectionID).all()
    return jsonify(Books = [b.serialize for b in books])








app.secret_key = '''
    \xa4hH\x8d\xf9\x8f\xd3%\xc1\xa0Kx06]Nx83[\xee\xf7\xa1F0\xd4\xc9\xc6]\xf4
    '''


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
