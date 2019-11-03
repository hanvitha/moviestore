import os
from flask import Flask, render_template, session, redirect, request, url_for, jsonify

# from flaskext.mysql import MySQL
import traceback
import logging
from utils.recommendations import Recommendation
import mysql.connector
from datetime import timedelta

__author__ = 'hanvitha'

app = Flask(__name__)
app.static_folder = 'static'
# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_Blah"gd5HK\n\xec]/'
app.logger.setLevel(logging.DEBUG)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
# APP_ROOT = "/opt/app-root/src/aahack"
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# DB connection details
# host="mysql.registration.svc"
host = "localhost"
port = '3306'
user = "root"
password = "rootpass"
database = "ms"

@app.route("/")
def index(error=None):
    if 'userid' in session:
        return redirect(url_for('home'))
    else:
        session.clear()
        return render_template("index.html", error=error)


@app.route("/login", methods=["POST"])
def login():
    email = request.form['login_user']
    password = request.form['login_password']
    # db, cursor = connectToDB()
    try:
        userquery = f"select id, name from users where email='{email}' and password='{password}';"
        cursor.execute(userquery)
        if cursor.rowcount > 0:
            userrecord = cursor.fetchone()
            session['userid'] = userrecord[0]
            session['email'] = email
            session['name'] = userrecord[1]
            print("session variables done!" + str(session['userid']) + " " + str(session['name']))
            return redirect(url_for('home'))
        else:
            return render_template("index.html", error="Invalid credentials")
    except Exception as e:
        logging.exception("Login error")


@app.route("/home", methods=["GET"])
def home():
    try:
        print("Session is " + session['name'])
        if 'userid' in session:
            print("Welcome home babe")
            trending = []
            message = "Welcome " + session['name']
            db, cursor = connectToDB()
            similarMovies = None
            latestmovie = None

            try:
                trending = recommObject.getTrendingRecommendations()
                if 'latestmovie' in session:
                    latestmovie = session['latestmovie']
                    print(latestmovie)
                    # moviequery = f"select title from movies where id='{latestmovie}';"
                    # cursor.execute(moviequery)
                    # if cursor.rowcount >0:
                    #     movierec = cursor.fetchone()
                    #     moviename = movierec[0]

                    similarMovies = recommObject.getContentBasedRecomm(latestmovie).head(15)
                    # similarMovies = pd.DataFrame({'movieid':simMoviesSeries.index, 'title':simMoviesSeries.values})
                    # similarMovies = simMoviesSeries.to_frame().rename(columns={0:'id'})
                    print(similarMovies.head(10))
                    similarMovies = similarMovies.values.tolist()
                    print(similarMovies)
            except Exception as e:
                traceback.print_exc()
            finally:
                return render_template("home.html", trending=trending, similarMovies=similarMovies, message=message)
        else:
            return render_template("index.html", error="Login Required to access the website")
    except Exception as e:
        traceback.print_exc()
        logging.exception("Home page error")


@app.route("/signup", methods=["POST"])
def signup():
    try:
        name = request.form['signup_name']
        password = request.form['signup_password']
        email = request.form['signup_email']
        zipcode = request.form['signup_zipcode']
        age = request.form['signup_age']
        # db, cursor = connectToDB()

        userquery = f"select id from users where email='{email}';"
        cursor.execute(userquery)
        if cursor.rowcount > 0:
            return render_template("index.html", error="Email ID already in use!")

        userquery = f"insert into users (id, password, name, email, zipcode, age) values (default, '{password}','{name}', '{email}', '{zipcode}', '{age}');"
        cursor.execute(userquery)
        db.commit()
        try:
            userquery = f"select id from users where email='{email}';"
            cursor.execute(userquery)
            if cursor.rowcount > 0:
                session["userid"] = cursor.fetchone()[0]
                session["email"] = email
                session["name"] = name
                return redirect(url_for("home"))
        except Exception as e:
            logging.exception("Signing in after signup error")
    except Exception as e:
        traceback.print_exc()
        logging.exception("Signup error external")


def connectToDB():
    db = mysql.connector.connect(host=host,
                                 user=user,
                                 password=password,
                                 database=database,
                                 port=port
                                 )
    cursor = db.cursor(buffered=True)
    return db, cursor


@app.route('/profile')
def profile():
    if 'userid' not in session:
        return render_template("index.html", error="Login required to access website!")

    return render_template('profile.html', name=session['name'], email=session['email'])


@app.route('/movie', methods=["GET"])
def movie():
    if 'userid' not in session:
        return render_template("index.html", error="Login required to access website!")

    try:
        movieid = request.args.get('id')
        print("ID is" + movieid)
        db, cursor = connectToDB()
        cursor.execute(f"select * from  movies where id='{movieid}';")
        movieRecord = cursor.fetchone()
        # print(movieRecord)
        if (not movieRecord):
            redirect(url_for('home'))
        moviename = movieRecord[1]
        year = movieRecord[2]
        overview = movieRecord[4]
        cursor.execute(f"select genreid from  movie_genres where movieid='{movieid}';")
        genreid = cursor.fetchone()
        genres = []
        while genreid is not None:
            # print(genreid)
            cursor.execute(f"select name from  genres where id='{genreid[0]}';")
            genre = cursor.fetchone()[0]
            # print(genre)
            genres.append(genre)
            genreid = cursor.fetchone()

        cursor.execute(f"select count(*) from  ratings where movieid='{movieid}';")
        count = cursor.fetchone()[0]

        cursor.execute(f"select ROUND(AVG(rating), 1) from  ratings where movieid='{movieid}';")
        rating = cursor.fetchone()[0]
        if (not rating):
            rating = 0
            count = 1
        # print(rating)
        return render_template('movie.html', movie=moviename, movieid=movieid, year=year, genres=genres, count=count, rating=rating, overview=overview)
    except Exception as e:
        traceback.print_exc()
        logging.exception("Movie page error")


@app.route('/watchmovie', methods=["POST","GET"])
def watchmovie():
    if 'userid' not in session:
        return render_template("index.html", error="Login required to access website!")
    else:
        if request.method=="POST":
            movie = request.form['movie']
        else:
            movie = request.args.get('movie')
        session['latestmovie'] = movie
        return render_template('watchmovie.html')


@app.route('/watchbygenre', methods=['GET'])
def watchbygenre():
    if 'userid' not in session:
        return render_template("index.html", error="Login required to access website!")
    else:
        try:
            genreid = request.args.get('genre')
            cursor.execute(f"select name from genres where id={genreid}")
            genreName = cursor.fetchone()[0]
            print('Watching by genre '+genreName)
            movies = recommObject.getMoviesByGenre(genreid, cursor)
            # print(movies)
            return render_template('genres.html', genreName=genreName, moviesByGenre=movies)
        except Exception as e:
            traceback.print_exc()
            return render_template('genres.html',genreName=None, moviesByGenre=None)

@app.route('/submitrating', methods=["POST"])
def submitrating():
    try:
        rating = request.form['rating']
        movieid = request.form['movieid']
        print(rating)
        print(movieid)
        query = "insert into ratings (id, userid, movieid, rating) values (default, %s,%s,%s );"

        print(query, (session['userid'], movieid, rating))
        cursor.execute(query, (session['userid'], movieid, rating))
        db.commit()
        return jsonify({'response': 'submitted response'})
    except:
        traceback.print_exc()
        return jsonify({'oops! something went wrong. Try again!'})


@app.route('/logout')
def logout():
    session.pop('userid', None)
    session.pop('name', None)
    session.pop('email', None)
    session.pop('latestmovie  ', None)
    session.clear()
    return redirect(url_for('index'))


db, cursor = connectToDB()
recommObject = Recommendation(db)
recommObject.prepareContentBasedRecomm()

if __name__ == '__main__':
    logout()
    app.run(debug=True)
