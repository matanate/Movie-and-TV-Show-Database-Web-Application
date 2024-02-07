from functools import wraps
from math import ceil
import datetime
import os

from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    abort,
    jsonify,
)
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, migrate
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from sqlalchemy.orm import relationship
from sqlalchemy.event import listens_for


# API key and secret key
API_KEY = os.environ.get("API_KEY")
SECRET_KEY = os.environ.get("SECRET_KEY")
API_HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {API_KEY}",
}
DB_URL = os.environ.get("DB_URL")

# Flask app setup
app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY

app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# User model with relationship to Reviews
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

    review = relationship("Reviews", back_populates="author")


# Titles model with relationship to Reviews
class Titles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), unique=False, nullable=False)
    release_date = db.Column(db.DateTime, unique=False, nullable=False)
    overview = db.Column(db.String(200), unique=False, nullable=False)
    genre_ids = db.Column(db.PickleType, unique=False, nullable=False)
    img_url = db.Column(db.String(200), unique=False, nullable=False)
    movie_or_tv = db.Column(db.String(20), unique=False, nullable=False)
    ratings = db.Column(db.Float(1), default=0.0)  # Average rating for the title

    review = relationship("Reviews", back_populates="title")

    @property
    def average_rating(self):
        # Calculate the average rating for the title
        total_ratings = sum(review.rating for review in self.review)
        num_reviews = len(self.review)
        avg_rating = total_ratings / num_reviews if num_reviews > 0 else 0.0
        return round(avg_rating, 1)


# Reviews model with relationships to Users and Titles
class Reviews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("Users", back_populates="review")
    title_id = db.Column(db.Integer, db.ForeignKey("titles.id"))
    title = relationship("Titles", back_populates="review")
    rating = db.Column(db.Float(1), unique=False, nullable=False)
    comment = db.Column(db.String(200), unique=False, nullable=False)
    date_posted = db.Column(db.DateTime, unique=False, nullable=False)


# Listen for the before_commit event to update average ratings
@listens_for(db.session, "before_commit")
def before_commit(session):
    for obj in session.new:
        # Check if the object being committed is a Review and has a title
        if isinstance(obj, Reviews) and obj.title:
            # Update the average rating for the corresponding Title
            obj.title.ratings = obj.title.average_rating

    for obj in session.deleted:
        # Check if the object being committed is a Review and has a title
        if isinstance(obj, Reviews) and obj.title:
            # Update the average rating for the corresponding Title
            obj.title.ratings = obj.title.average_rating

    for obj in session.dirty:
        # Check if the object being committed is a Review and has a title
        if isinstance(obj, Reviews) and obj.title:
            # Update the average rating for the corresponding Title
            obj.title.ratings = obj.title.average_rating


# Set Login manager
login_manager = LoginManager()
login_manager.init_app(app)

# Fetching movie and TV genres from TMDB API
movie_genres = requests.get(URL_MOVIE_GENERS, headers=API_HEADERS).json()["genres"]
tv_genres = requests.get(URL_TV_GENERS, headers=API_HEADERS).json()["genres"]
genres_dict = {}
for genre in movie_genres:
    genres_dict[genre["id"]] = genre["name"]
for genre in tv_genres:
    genres_dict[genre["id"]] = genre["name"]


# Function to fetch titles from TMDB API based on search query
def fetch_titles_from_api(movie_or_tv, title):
    # Construct the API URL for searching titles based on the provided parameters
    url = f"https://api.themoviedb.org/3/search/{movie_or_tv}?query={title}&include_adult=false&language=en-US&page=1"

    try:
        # Make a GET request to the TMDB API with the specified headers
        response = requests.get(url, headers=API_HEADERS)

        # Raise an exception for HTTP errors
        response.raise_for_status()

        # Parse the JSON response and extract the results
        response = response.json()["results"]

        # Initialize an empty list to store the extracted title information
        titles_list = []

        # Loop through each title in the API response
        for title in response:
            # Determine the key names based on the movie_or_tv parameter
            if movie_or_tv == "movie":
                release_date_text = "release_date"
                title_text = "title"
            elif movie_or_tv == "tv":
                release_date_text = "first_air_date"
                title_text = "name"

            # Create a dictionary with relevant title information and append it to the list
            titles_list.append(
                {
                    "id": title["id"],
                    "title": title[title_text],
                    "release_date": title[release_date_text],
                    "overview": title["overview"],
                    "img_url": f"https://www.themoviedb.org/t/p/w600_and_h900_bestv2{title['poster_path']}",
                    "genre_ids": title["genre_ids"],
                }
            )
            # Return the list of titles
            return titles_list

    # Handle exceptions related to the API request
    except requests.RequestException as e:
        print(f"Error during API request: {e}")
        # Abort the request and return a 500 Internal Server Error status
        abort(500)


# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


# Context processor for injecting variables into templates
@app.context_processor
def inject_vars():
    # Inject the 'current_user' and 'year' variables into the template context
    return dict(current_user=current_user, year=datetime.datetime.now().year)


# Decorator for restricting access to admin-only routes
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the current user is an admin (user ID 1)
        if current_user.id != 1:
            # If not an admin, abort the request with a 403 Forbidden status
            return abort(403)

        # If the current user is an admin, proceed with the original function
        return f(*args, **kwargs)

    # Return the decorated function
    return decorated_function


# Route for the homepage
@app.route("/")
def home():
    # Query all titles from the database
    all_titles = db.session.query(Titles).all()

    # Get the top 10 movies based on ratings
    top_movies = (
        db.session.query(Titles)
        .filter_by(movie_or_tv="movie")
        .order_by(Titles.ratings.desc())
        .limit(10)
        .all()
    )
    # Get the top 10 tv shows based on ratings
    top_tvs = (
        db.session.query(Titles)
        .filter_by(movie_or_tv="tv")
        .order_by(Titles.ratings.desc())
        .limit(10)
        .all()
    )

    # Create a dictionary with top movies and TV shows
    top_titles = {"Movies": top_movies, "TV Shows": top_tvs}

    # Render the homepage template with title information
    return render_template(
        "homepage.html",
        all_titles=all_titles,
        top_titles=top_titles,
    )


# Route for user signup
@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        # Retrieve user input from the signup form
        name = request.form.get("InputName")
        email = request.form.get("InputEmail")
        password = request.form.get("InputPassword")
        user = db.session.execute(db.select(Users).where(Users.email == email)).first()

        # Check if the user with the given email already exists
        if user:
            # If the user already exists, flash a warning and redirect to the login page
            flash("That email already exist, please Login.", "warning")
            return redirect(url_for("login"))
        else:
            # Create a new user and add them to the database
            user = Users(
                name=name,
                email=email,
                password=generate_password_hash(
                    password,
                    method="pbkdf2:sha256",
                    salt_length=16,
                ),
            )
            db.session.add(user)
            db.session.commit()

            # Log in the newly created user
            login_user(user)

            # Redirect to the homepage
            return redirect(url_for("home"))

    # Render the signup form template
    return render_template("signup.html")


# Route for user login
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        # Retrieve user input from the login form
        email = request.form.get("InputEmail")
        password = request.form.get("InputPassword")

        # Use the query method to get the user object
        user = Users.query.filter_by(email=email).first()

        if not user:
            # If the user does not exist, flash a warning and redirect to the login page
            flash("That email does not exist, please try again.", "warning")
            return redirect(url_for("login"))
        elif not check_password_hash(user.password, password):
            # If the password is incorrect, flash a warning and redirect to the login page
            flash("Password incorrect, please try again.", "warning")
            return redirect(url_for("login"))
        else:
            # If login is successful, log in the user and redirect to the homepage
            login_user(user)
            flash(f"Welcome {user.name}, you are now logged in.", "success")
            return redirect(url_for("home"))

    # Render the login form template
    return render_template("login.html")


# Route for user logout
@app.route("/logout")
def logout():
    # Flash a logout message, log out the user, and redirect to the homepage
    flash(f"Goodbye {current_user.name}, you are now logged out.", "success")
    logout_user()
    return redirect(url_for("home"))


# Route for adding titles (admin only)
@app.route("/add", methods=["POST", "GET"])
@admin_only
def add():
    if request.method == "POST":
        # Retrieve user input from the add title form
        movie_or_tv = request.form.get("InputMovieOrTV")
        title = request.form.get("InputTitle")

        # Redirect to the title selection page with the specified parameters
        return redirect(url_for("select", title=title, movie_or_tv=movie_or_tv))

    # Render the add title form template
    return render_template("add.html")


# Route for selecting a title from search results (admin only)
@app.route("/select", methods=["POST", "GET"])
@admin_only
def select():
    # Retrieve title and movie_or_tv parameters from the request arguments
    title = request.args.get("title")
    movie_or_tv = request.args.get("movie_or_tv")

    # Fetch titles from the TMDB API based on the provided parameters
    titles_list = fetch_titles_from_api(movie_or_tv, title)

    if request.method == "POST":
        # Retrieve the selected title ID from the form
        title_id = int(request.form.get("action"))
        selected_title = titles_list[title_id]

        # Check if the selected title already exists in the database
        if not db.session.get(Titles, selected_title.get("id")):
            # If not, create a new Titles object and add it to the database
            title_obj = Titles(
                id=selected_title.get("id"),
                title=selected_title.get("title"),
                release_date=datetime.datetime.strptime(
                    selected_title.get("release_date"), "%Y-%m-%d"
                ),
                overview=selected_title.get("overview"),
                img_url=selected_title.get("img_url"),
                genre_ids=selected_title.get("genre_ids"),
                movie_or_tv=movie_or_tv,
            )
            db.session.add(title_obj)
            db.session.commit()
            flash("Title added successfully.", "success")
            return redirect(url_for("home"))
        else:
            # If the title already exists, flash a warning message
            flash("Title already exists in the database.", "warning")

    # Enumerate titles_list if it's not empty
    if titles_list:
        titles_list = enumerate(titles_list)

    # Render the title selection template with the fetched titles
    return render_template("select.html", titles_list=titles_list)


if __name__ == "__main__":
    app.run(debug=True)
