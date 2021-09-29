from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

#the movie database api, this is my api key, replace with your own.
API_key  = '56d007c31ed986ca2947af65179cca97'
url = 'https://api.themoviedb.org/3/search/movie/'

MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

#replace this secret key with your own
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

##create DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#create database of movies
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)
db.create_all()

#testing the code to see if the database has been created
# newmovie = Movie(
#     title = "No Country For Old Men",
#     year = 2007,
#     description = "A hunter's life takes a drastic turn when he discovers two million dollars while strolling through the aftermath of a drug deal. He is then pursued by a psychopathic killer who wants the money.",
#     rating = 8.5,
#     ranking = 1,
#     review = 'A masterpiece carried by its brilliant casting. Anton Chigurh is one of the all-time cinema villains.',
#     img_url = 'https://static.rogerebert.com/uploads/movie/movie_poster/no-country-for-old-men-2007/large_6o0UWX2naW7HK45PDNYmoMIk5qs.jpg'
# )
# db.session.add(newmovie)
# db.session.commit()

#display the landing page using flask
@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        # This line gives each movie a new ranking reversed from their order in all_movies
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies = all_movies)


class RateMovieForm(FlaskForm):
    rating = StringField("Your Rating Out of 10")
    review = StringField("Your Review")
    submit = SubmitField("Done")

@app.route("/edit", methods = ["GET", "POST"])
def rate_movie():
    form = RateMovieForm()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return(render_template("edit.html", movie = movie, form = form))

class FindMovieForm(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")


@app.route("/add", methods=["GET", "POST"])
def add_movie():
    form = FindMovieForm()

    if form.validate_on_submit():
        movie_title = form.title.data
        response = requests.get(url, params={"api_key": API_key, "query": movie_title})
        data = response.json()["results"]
        print(data)
        return render_template("select.html", options=data)

    return render_template("add.html", form=form)

@app.route("/delete")
def delete_movie():
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))


#
@app.route("/find")
def find_movie():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        movie_api_url = f"{MOVIE_DB_INFO_URL}/{movie_api_id}"
        response = requests.get(movie_api_url, params={"api_key": API_key, "language": "en-US"})
        data = response.json()
        new_movie = Movie(
            title=data["title"],
            #removing the month and day from the date:
            year=data["release_date"].split("-")[0],
            img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",
            description=data["overview"]
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True)
