# Title: Movie and TV Show Database Web Application

## Overview

This is a Flask web application that serves as a movie and TV show database.
Users can sign up, log in, search for titles, view details of individual titles,
add reviews, and explore the top-rated movies and TV shows. Additionally,
administrators have access to functionalities like adding and deleting titles.

## Features

- **User Authentication**: Users can sign up, log in, and log out securely.

- **Title Exploration**: Users can view a list of all movies, all TV shows, or
  search for specific titles.

- **Title Details**: Users can view details of individual titles, including
  average ratings, genres, and user reviews.

- **Reviews**: Users can add, edit, and delete their reviews for specific
  titles.

- **Top-Rated Titles**: The homepage displays the top 10 movies and TV shows
  based on ratings.

- **Administrative Functions**: Admins can add new titles to the database and
  delete existing titles.

## Dependencies

- Flask: A web framework for Python.
- Flask-SQLAlchemy: An extension for Flask that simplifies database integration.
- Flask-Migrate: A Flask extension for handling database migrations.
- Flask-Login: Provides user session management.
- Requests: Simplifies HTTP requests to the
  [TMDB API](developer.themoviedb.org).
- Werkzeug: Handles user password hashing.

## Setup

1. **Environment Variables**: Ensure the following environment variables are
   set:

   - `API_KEY`: API key for The Movie Database (TMDB Access Token Auth).
   - `SECRET_KEY`: Secret key for Flask application (Any key you would choose).
   - `DB_URL`: URL for the SQLAlchemy database. (SQLite: "sqlite:///db_name.db",
     PostgreSQL: "postgresql://username:password@localhost:5432/db_name" etc.)

2. **Install Dependencies**: Run
   `pip install Flask Flask-SQLAlchemy Flask-Migrate Flask-Login requests`.

3. **Database Migration**: Run the following commands to apply database
   migrations:

   ```bash
   flask db upgrade
   ```

4. **Run the Application**: Execute `python app.py` to start the Flask
   application.

5. **Access the Application**: Open a web browser and navigate to
   `http://127.0.0.1:5000/`.

## Usage

1. **Homepage**: Explore the top-rated movies and TV shows.

2. **Sign Up**: Create an account to access additional features.

3. **Log In**: Existing users can log in to the application.

4. **Search Titles**: Use the search bar to find specific movies or TV shows.

5. **View Title Details**: Click on a title to see more details, including
   reviews.

6. **Add Reviews**: Logged-in users can add, edit, and delete their reviews for
   titles.

7. **Admin Functions**: Admins can add new titles and delete existing titles
   (the admin is the first user to sign up).

## Deployment (Live Demo)

Check out the live demo:
[Live Demo](https://movietv-yjhw.onrender.com)

## Acknowledgments

This web application relies on data from The Movie Database (TMDB). Thanks to
TMDB for providing an API that allows access to movie and TV show information.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file
for details.
