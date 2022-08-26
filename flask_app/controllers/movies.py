from flask_app import app, db, render_template, request, redirect, make_response, bcrypt, session, flash, url_for, requests, os, verify_logged_in
from models import User, Movie, Post, Comment, favorites, post_likes, comment_likes, faved
import tmdbsimple as tmdb
tmdb.API_KEY = f"{os.getenv('API_KEY')}"


@app.route('/<int:id>')
def movie_posts(id):
    upms = db.session.query(User, Post, Movie).select_from(User).join(
        Post).join(Movie).where(Post.user_id == User.id and Post.movie_id == Movie.id).filter(Movie.tmdb_id == id).all()
    print(upms)
    return render_template('feed.html', upms=upms, movie=upms[0][2], faved=faved(id), truncate=True, title=f"{upms[0][2].title} Posts | ReDirector")


@app.route('/<int:id>/<string:type>')
def movie_posts_by_type(id, type):
    upms = db.session.query(User, Post, Movie).select_from(User).join(
        Post).join(Movie).where(Post.user_id == User.id and Post.movie_id == Movie.id).filter(Movie.tmdb_id == id).filter(Post.type == type).all()
    return render_template('feed.html', movie=upms[0][2], faved=faved(id), upms=upms, truncate=True, title=f"{type} Posts | {upms[0][2].title} | ReDirector")


@app.route('/movies')
def all_movies():
    movies = Movie.query.all()
    return render_template('pickmovie.html', movies=movies, title='All Movies | ReDirector')


@app.route("/search", methods=["POST"])
def search():
    search = tmdb.Search()
    response = search.movie(query=f"{request.form['query']}")
    return render_template('pickmovie.html', movies=search.results, posting=True, title="Movie Search | ReDirector")


@app.route('/movie/add/<int:id>')
def add_movie(id):
    movie_in_db = Movie.query.filter_by(tmdb_id=id).first()
    print(movie_in_db)
    if not movie_in_db:
        movie = tmdb.Movies(id)
        response = movie.info()
        title = movie.title
        description = movie.overview
        date = movie.release_date[:4]
        genres = movie.genres
        genre = ''
        for g in genres:
            if g != genres[0]:
                genre += ' / '
            genre += g['name']
        imdb_id = movie.imdb_id
        poster_path = movie.poster_path
        response = movie.releases()
        for c in movie.countries:
            if c['iso_3166_1'] == 'US':
                rating = c['certification']
        new_movie = Movie(title, description,
                          date, rating, genre, imdb_id, id, poster_path)
        db.session.add(new_movie)
        db.session.commit()
        return render_template('newpost.html', title='New Post | ReDirector', movie=new_movie)
    else:
        return render_template('newpost.html', title='New Post | ReDirector', movie=movie_in_db)


@app.route('/fav/add/<int:id>')
def add_favorite(id):
    if not 'user_id' in session:
        return redirect
    user = User.query.filter_by(id=session['user_id']).first()
    movie = Movie.query.filter_by(id=id).first()
    if movie in user.favorites:
        return make_response(render_template("404.html"), 404)
    user.favorites.append(movie)
    db.session.commit()
    return redirect(request.referrer)


@app.route('/fav/remove/<int:id>')
def remove_favorite(id):
    user = User.query.filter_by(id=session['user_id']).first()
    movie = Movie.query.filter_by(id=id).first()
    if not movie in user.favorites:
        return make_response(render_template("404.html"), 404)
    user.favorites.remove(movie)
    db.session.commit()
    return redirect(request.referrer)
