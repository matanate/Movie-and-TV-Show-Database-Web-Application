from functools import wraps
import os

from flask import (
    Flask,
)
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, migrate
from flask_login import UserMixin
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


if __name__ == "__main__":
    app.run(debug=True)
