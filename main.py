from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

API_KEY = 'f954280cf27e83ce9aee6a43e4559918'

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////study/python_bootcamp_2/Day64_MyTop10Movies/movies_list.db"
db = SQLAlchemy(app)


class RatingForm(FlaskForm):
    rating = StringField(label="Your rating out of 10 eg. 7.4", validators=[DataRequired()])
    review = StringField(label="Your Review", validators=[DataRequired()])
    submit = SubmitField(label="Done")


class AddForm(FlaskForm):
    title = StringField(label="Movie Title", validators=[DataRequired()])
    submit = SubmitField(label="Add Movie")


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False, unique=True)
    year = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(5000), nullable=False)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(1000))
    img_url = db.Column(db.String(1000), nullable=False)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    with app.app_context():
        all_movies = db.session.query(Movie).all()

    return render_template("index.html", all_movies=all_movies)


@app.route('/edit/<movie_id>', methods=['GET', 'POST'])
def edit(movie_id):
    form = RatingForm()
    with app.app_context():
        movie = Movie.query.get(movie_id)
    if request.method == 'POST':
        with app.app_context():
            movie = Movie.query.get(movie_id)
            movie.rating = request.form['rating']
            movie.review = request.form['review']
            db.session.commit()
        return redirect("/")

    return render_template('edit.html', movie=movie, form=form)


@app.route('/delete/<movie_id>')
def delete(movie_id):
    with app.app_context():
        movie = Movie.query.get(movie_id)
        db.session.delete(movie)
        db.session.commit()
        return redirect("/")


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = AddForm()
    if request.method == 'POST':
        title = request.form['title']
        response = requests.get(f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&language=en-US&query={title}")
        response.raise_for_status()
        data = response.json()['results']
        return render_template('select.html', data=data)

    return render_template('add.html', form=form)


@app.route('/select/<movie_i>')
def select(movie_i):
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_i}?api_key={API_KEY}&language=en-US")
    response.raise_for_status()
    data = response.json()
    with app.app_context():
        new_movie = Movie(
            title=data['original_title'],
            year=data['release_date'],
            description=data['overview'],
            rating=0,
            ranking=0,
            review='None',
            img_url=f"https://image.tmdb.org/t/p/w500/{data['poster_path']}"
        )
        db.session.add(new_movie)
        db.session.commit()
        movie = Movie.query.filter_by(title=data['original_title']).first()
        print(movie.id)
    return redirect(url_for('edit', movie_id=movie.id))


if __name__ == '__main__':
    app.run(debug=True)
