from flask_app import app, db, render_template, request, redirect, bcrypt, session, flash, url_for, verify_logged_in, datetime, timedelta
from models import User, Movie, Post, Comment, favorites, post_likes, comment_likes, faved
import random

names = ['kangaroo', 'lobster', 'shark', 'pizza',
         'grapefruit', 'ostrich', 'zeppelin', 'cheese', 'ninja']


@app.route('/new/post', methods=['POST', 'GET'])
def new_post():
    if not 'user' in session:
        return redirect('/')
    if request.method == 'POST':
        if not Post.validate_post(request.form):
            print('Invalid form')
            return render_template('pickmovie.html', title="Movie Search | ReDirector")
        type = request.form['type']
        title = request.form['title']
        content = request.form['content']
        user_id = session['user_id']
        movie_id = request.form['id']
        post = Post(type, title, content, user_id, movie_id, datetime.now())
        db.session.add(post)
        db.session.commit()
        post_id = post.id
        return redirect(f"/post/{post_id}")
    else:
        return render_template('pickmovie.html', title="Movie Search | ReDirector")


@app.route('/comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    content = request.form['content']
    comment = Comment(
        content, session['user_id'], post_id, random.choice(names), datetime.now())
    db.session.add(comment)
    db.session.commit()
    return redirect(f"/post/{post_id}")


@app.route('/post/<int:id>')
def view_post(id):
    upms = db.session.query(User, Post, Movie).select_from(User).join(
        Post).join(Movie).where(Post.user_id == User.id and Post.movie_id == Movie.id).filter(Post.id == id).order_by(Post.created_at.desc()).all()
    # Set post timestamp
    for upm in upms:
        delta = (datetime.now() - upm[1].created_at)
        seconds = delta.seconds
        minutes = f"{seconds//60} min. ago"
        hours = f"{seconds//3600} hr. ago"
        days = f"{delta.days} d. ago"
        weeks = f"{delta.days//7} wk. ago"
        for unit in [weeks, days, hours, minutes]:
            if int(unit[:1]) > 0:
                upm[1].time_since = unit
                break
    comments = db.session.query(Comment).filter(
        Comment.post_id == id).order_by(Comment.created_at).all()
    # Set comment timestamps
    for comment in comments:
        delta = (datetime.now() - comment.created_at)
        seconds = delta.seconds
        minutes = f"{seconds//60} min. ago"
        hours = f"{seconds//3600} hr. ago"
        days = f"{delta.days} d. ago"
        weeks = f"{delta.days//7} wk. ago"
        for unit in [weeks, days, hours, minutes]:
            if int(unit[:1]) > 0:
                comment.time_since = unit
                break
    return render_template('feed.html', upms=upms, movie=upms[0][2], comments=comments, truncate=False, faved=faved(upms[0][2].tmdb_id), title=f"{upms[0][2].title} | ReDirector")


@app.route('/<string:type>')
def view_posts_by_type(type):
    upms = db.session.query(User, Post, Movie).select_from(User).join(
        Post).join(Movie).where(Post.user_id == User.id and Post.movie_id == Movie.id).filter(Post.type == type).order_by(Post.created_at.desc()).all()
    # Set post timestamp
    for upm in upms:
        delta = (datetime.now() - upm[1].created_at)
        seconds = delta.seconds
        minutes = f"{seconds//60} min. ago"
        hours = f"{seconds//3600} hr. ago"
        days = f"{delta.days} d. ago"
        weeks = f"{delta.days//7} wk. ago"
        for unit in [weeks, days, hours, minutes]:
            if int(unit[:1]) > 0:
                upm[1].time_since = unit
                break
    return render_template('feed.html', upms=upms, truncate=True, title=f"{type} Posts | ReDirector")


@app.route('/<int:user_id>/posts')
def view_posts_by_user(user_id):
    upms = db.session.query(User, Post, Movie).select_from(User).join(
        Post).join(Movie).where(Post.user_id == User.id and Post.movie_id == Movie.id).filter(Post.user_id == user_id).order_by(Post.created_at.desc()).all()
    # Set post timestamp
    for upm in upms:
        delta = (datetime.now() - upm[1].created_at)
        seconds = delta.seconds
        minutes = f"{seconds//60} min. ago"
        hours = f"{seconds//3600} hr. ago"
        days = f"{delta.days} d. ago"
        weeks = f"{delta.days//7} wk. ago"
        for unit in [weeks, days, hours, minutes]:
            if int(unit[:1]) > 0:
                upm[1].time_since = unit
                break
    my = f"{upms[0][0].username}'s "
    if 'user_id' in session and user_id == session['user_id']:
        my = 'My '
    return render_template('feed.html', upms=upms, truncate=True, user_id=user_id, title=my+"Posts | ReDirector")


@app.route('/<int:user_id>/posts/<string:type>')
def view_posts_by_user_and_type(user_id, type):
    upms = db.session.query(User, Post, Movie).select_from(User).join(
        Post).join(Movie).where(Post.user_id == User.id and Post.movie_id == Movie.id).filter(Post.user_id == user_id).filter(Post.type == type).order_by(Post.created_at.desc()).all()
    # Set post timestamp
    for upm in upms:
        delta = (datetime.now() - upm[1].created_at)
        seconds = delta.seconds
        minutes = f"{seconds//60} min. ago"
        hours = f"{seconds//3600} hr. ago"
        days = f"{delta.days} d. ago"
        weeks = f"{delta.days//7} wk. ago"
        for unit in [weeks, days, hours, minutes]:
            if int(unit[:1]) > 0:
                upm[1].time_since = unit
                break
    my = None
    if 'user_id' in session and user_id == session['user_id']:
        my = 'My '
    return render_template('feed.html', upms=upms, truncate=True, title=my + "Posts | ReDirector")


@app.route('/categories')
def categories():
    return render_template('categories.html')
