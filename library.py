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
        # 2DO - Crappy way to stop SQLAlchemy from adding the same id value
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



# R - BOOKS
@app.route('/collections/<int:collectionID>/books/')
def showBooksInCollection(collectionID):
    collection = session.query(Collections).filter_by(id=collectionID).one()
    books      = session.query(Books).filter_by(collectionID=collectionID).all()
    return render_template('collection.html', collection=collection, books=books)

# R - A BOOK
@app.route('/collections/<int:collectionID>/books/<int:bookID>/')
def showBook(collectionID, bookID):
    return "This page will show book " + str(bookID) + " in collection " + str(collectionID) + "."

# C - BOOKS
@app.route('/collections/<int:collectionID>/books/create/', methods=['GET', 'POST'])
def createBook(collectionID):
    return "This page will create a book in collection " + str(collectionID) + "."

# U - BOOKS
@app.route('/collections/<int:collectionID>/books/<int:bookID>/edit/', methods=['GET', 'POST'])
def editBook(collectionID, bookID):
    return "This page will edit book " + str(bookID) + " in collection " + str(collectionID) + "."

# D - BOOKS
@app.route('/collections/<int:collectionID>/books/<int:bookID>/delete/', methods=['GET', 'POST'])
def deleteBook(collectionID, bookID):
    return "This page will delete book " + str(bookID) + " in collection " + str(collectionID) + "."





app.secret_key = '''
    \xa4hH\x8d\xf9\x8f\xd3%\xc1\xa0Kx06]Nx83[\xee\xf7\xa1F0\xd4\xc9\xc6]\xf4
    '''


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
