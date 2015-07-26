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


# 2DO - Establish client id and client secret
# CLIENT_ID = json.loads(
#     open('client_secrets.json', 'r').read())['web']['client_id']
# APPLICATION_NAME = "Restaurants R' Us"

# Create session to talk to database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///theArchives.db'
engine = create_engine('postgres://ewcuvsjxbhzuce:lTxnaKjAsx3L5JVCsjN1NXrrnS@ec2-54-83-20-177.compute-1.amazonaws.com:5432/d6l2vgh7udooqv')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()



# LOGIN
@app.route('/login/')
def login():
    return "This will be the login page."



# R - COLLECTIONS / HOMEPAGE
@app.route('/')
@app.route('/collections/')
def homePage():
    collections = session.query(Collections).all()
    return render_template('index.html', collections=collections)

# C - COLLECTIONS
@app.route('/collections/create/', methods=['GET', 'POST'])
def createCollections():
    collections = session.query(Collections).all()
    if request.method == 'POST':
        collection = Collections(
            name = request.form['name'],
            # 2DO - Change once ability to login is added
            patronID = 1
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
    return render_template('collection.html', collections=collections, collection=collection, books=books)

# R - A BOOK
@app.route('/collections/<int:collectionID>/books/<int:bookID>/')
def showBook(collectionID, bookID):
    collections = session.query(Collections).all()
    collection  = session.query(Collections).filter_by(id=collectionID).one()
    book        = session.query(Books).filter_by(id=bookID).one()
    return render_template('book.html', collections=collections, collection=collection, book=book)

# C - BOOKS
@app.route('/collections/<int:collectionID>/books/add/', methods=['GET', 'POST'])
def addBook(collectionID):
    collections = session.query(Collections).all()
    currentCollection = session.query(Collections).filter_by(id=collectionID).one()
    if request.method == 'POST':
        book = Books(
            title        = request.form['title'],
            author       = request.form['author'],
            genre        = request.form.get('genre'),
            coverImage   = request.form.get('coverImage'),
            description  = request.form.get('description'),
            collectionID = collectionID,
            # 2DO - Change once ability to login is added
            patronID     = 1
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
