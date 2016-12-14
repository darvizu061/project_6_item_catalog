from flask import Flask, render_template, request, redirect, url_for, flash
from flask import jsonify, make_response
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Genre, BookItem, Base, User
import random
import string
import httplib2
import json
import requests
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

# --------------------------------------------------
#                App Configuration
# --------------------------------------------------
app = Flask(__name__)
engine = create_engine('sqlite:///books.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
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
        return user
    except:
        return None
# --------------------------------------------------
#                OAuth Login Routes
# --------------------------------------------------


@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('oauth_login.html',
                           STATE=state,
                           user=login_session)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
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

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('User is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if user exists. If not, make a new User account
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
    output += ''' "style="
               width: 300px;
               height: 300px;
               border-radius:150px;
               -webkit-border-radius: 150px;
               -moz-border-radius: 150px;">'''
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():

    access_token = login_session.get('credentials').access_token

    print 'In gdisconnect access token is %s' % access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    string = 'https://accounts.google.com/o/oauth2/revoke?token=%s'
    url = string % login_session.get('credentials').access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session.get('credentials').access_token
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:

        response = make_response(json.dumps('Failed to revoke token for user.',
                                 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# --------------------------------------------------
#                API ENDPOINT
# --------------------------------------------------
@app.route('/allgenres/JSON')
def genreJSON():
    genres = session.query(Genre).all()
    return jsonify(Genres=[i.serialize for i in genres])


@app.route('/genres/<int:genre_id>/books/JSON')
def genreBooksJSON(genre_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    books = session.query(BookItem).filter_by(genre_id=genre.id).all()
    return jsonify(Books=[i.serialize for i in books])


@app.route('/allbooks/JSON')
def allBooksJSON():
    books = session.query(BookItem).all()
    return jsonify(AllBooks=[i.serialize for i in books])


@app.route('/book/<int:book_id>/JSON')
def bookJSON(book_id):
    book = session.query(BookItem).filter_by(id=book_id).one()
    return jsonify(Book=book.serialize)


# --------------------------------------------------
#                Routes: Public
# --------------------------------------------------
@app.route('/')
def homepage():
    genres = session.query(Genre).all()
    print login_session.get('credentials')
    return render_template('homepage.html',
                           genres=genres,
                           user=login_session)


@app.route('/genre/<int:genre_id>/')
def genreBooks(genre_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    booksInGenre = session.query(BookItem).filter_by(genre_id=genre.id)
    return render_template('booksingenre.html',
                           genre=genre,
                           books=booksInGenre,
                           user=login_session)


# --------------------------------------------------
#                Routes: Private
# --------------------------------------------------
@app.route('/genre/new', methods=['GET', 'POST'])
def newGenre():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newGenre = Genre(name=request.form['name'],
                         user_id=login_session['user_id'])
        session.add(newGenre)
        session.commit()
        flash("new Genre created!")
        return redirect(url_for('homepage'))
    else:
        return render_template('genre_new.html',
                               user=login_session)


@app.route('/genre/<int:genre_id>/edit', methods=['GET', 'POST'])
def editGenre(genre_id):
    if 'username' not in login_session:
        return redirect('/login')
    editGenre = session.query(Genre).filter_by(id=genre_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editGenre.name = request.form['name']
        session.add(editGenre)
        session.commit()
        flash("Genre name has been edited!")
        return redirect(url_for('homepage'))
    else:
        editGenre = session.query(Genre).filter_by(id=genre_id).one()
        # If logged user is NOT the creater of the genre
        if editGenre.user_id != login_session['user_id']:
            return "ERROR: NOT AUTHORIZED"
        return render_template('genre_edit.html',
                               genre_id=genre_id,
                               i=editGenre,
                               user=login_session)


@app.route('/genre/<int:genre_id>/delete', methods=['GET', 'POST'])
def deleteGenre(genre_id):
    if 'username' not in login_session:
        return redirect('/login')
    deleteGenre = session.query(Genre).filter_by(id=genre_id).one()
    if request.method == 'POST':
        session.delete(deleteGenre)
        session.commit()
        flash("Genre has been deleted!")
        return redirect(url_for('homepage'))
    else:
        deleteGenre = session.query(Genre).filter_by(id=genre_id).one()
        # If logged user is NOT the creater of the genre
        if deleteGenre.user_id != login_session['user_id']:
            return "ERROR: NOT AUTHORIZED"
        return render_template('genre_delete.html',
                               genre_id=genre_id,
                               i=deleteGenre,
                               user=login_session)


@app.route('/genre/<int:genre_id>/new', methods=['GET', 'POST'])
def newBookItem(genre_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newBookItem = BookItem(name=request.form['name'],
                               description=request.form['description'],
                               price=request.form['price'],
                               author=request.form['author'],
                               year_published=request.form['year'],
                               genre_id=genre_id,
                               user_id=login_session['user_id'])
        session.add(newBookItem)
        session.commit()
        flash("New Book has been added!")
        return redirect(url_for('genreBooks',
                                genre_id=genre_id,
                                user=login_session))
    else:
        return render_template('book_new.html',
                               genre_id=genre_id,
                               user=login_session)


@app.route('/genre/<int:genre_id>/<int:book_item_id>/edit',
           methods=['GET', 'POST'])
def editBookItem(genre_id, book_item_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedBook = session.query(BookItem).filter_by(id=book_item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedBook.name = request.form['name']
            editedBook.description = request.form['description']
            editedBook.price = request.form['price']
            editedBook.author = request.form['author']
            editedBook.year_published = request.form['year']
        session.add(editedBook)
        session.commit()
        flash("Book has been edited!")
        return redirect(url_for('genreBooks', genre_id=genre_id))
    else:
        editedBook = session.query(BookItem).filter_by(id=book_item_id).one()
        if editedBook.user_id != login_session['user_id']:
            return "ERROR: NOT AUTHORIZED"
        return render_template('book_edit.html',
                               genre_id=genre_id,
                               book_item_id=book_item_id,
                               item=editedBook,
                               user=login_session)


@app.route('/genre/<int:genre_id>/<int:book_item_id>/delete',
           methods=['GET', 'POST'])
def deleteBookItem(genre_id, book_item_id):
    if 'username' not in login_session:
        return redirect('/login')
    deletedBook = session.query(BookItem).filter_by(id=book_item_id).one()
    if request.method == 'POST':
        session.delete(deletedBook)
        session.commit()
        flash("Book has been deleted!")
        return redirect(url_for('genreBooks', genre_id=genre_id))
    else:
        deletedBook = session.query(BookItem).filter_by(id=book_item_id).one()
        if deletedBook.user_id != login_session['user_id']:
            return "ERROR: NOT AUTHORIZED"
        return render_template('book_delete.html',
                               genre_id=genre_id,
                               book_item_id=book_item_id,
                               item=deletedBook,
                               user=login_session)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
