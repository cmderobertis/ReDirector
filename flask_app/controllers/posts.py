from flask_app import app, db, render_template, request, redirect, bcrypt, session, flash, url_for, verify_logged_in
from models import User, Movie, Post, Comment, favorites, post_likes, comment_likes, faved
# from flask_app.models.movie import Movie
# from flask_app.models.post import Post
# from flask_app.models.comment import Comment


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
        post = Post(type, title, content, user_id, movie_id)
        db.session.add(post)
        db.session.commit()
        post_id = post.id
        return redirect(f"/post/{post_id}")
    else:
        return render_template('pickmovie.html', title="Movie Search | ReDirector")


@app.route('/post/<int:id>')
def view_post(id):
    upms = db.session.query(User, Post, Movie).select_from(User).join(
        Post).join(Movie).where(Post.user_id == User.id and Post.movie_id == Movie.id).filter(Post.id == id).first()
    comments = db.session.query(Comment).filter(
        Comment.post_id == id).order_by(Comment.created_at).all()
    return render_template('feed.html', upms=[upms], movie=upms[2], comments=comments, truncate=False, faved=faved(upms[2].tmdb_id), title=f"{upms[2].title} | ReDirector")


@app.route('/<string:type>')
def view_posts_by_type(type):
    upms = db.session.query(User, Post, Movie).select_from(User).join(
        Post).join(Movie).where(Post.user_id == User.id and Post.movie_id == Movie.id).filter(Post.type == type).all()
    return render_template('feed.html', upms=upms, truncate=True, title=f"{type} Posts | ReDirector")


@app.route('/<int:user_id>/posts')
def view_posts_by_user(user_id):
    upms = db.session.query(User, Post, Movie).select_from(User).join(
        Post).join(Movie).where(Post.user_id == User.id and Post.movie_id == Movie.id).filter(Post.user_id == user_id).all()
    my = f"{upms[0][0].username}'s "
    if 'user_id' in session and user_id == session['user_id']:
        my = 'My '
    return render_template('feed.html', upms=upms, truncate=True, user_id=user_id, title=my+"Posts | ReDirector")


@app.route('/<int:user_id>/posts/<string:type>')
def view_posts_by_user_and_type(user_id, type):
    upms = db.session.query(User, Post, Movie).select_from(User).join(
        Post).join(Movie).where(Post.user_id == User.id and Post.movie_id == Movie.id).filter(Post.user_id == user_id).filter(Post.type == type).all()
    my = None
    if 'user_id' in session and user_id == session['user_id']:
        my = 'My '
    return render_template('feed.html', upms=upms, truncate=True, title=my + "Posts | ReDirector")


@app.route('/comment/<int:id>', methods=['POST'])
def add_comment(id):
    content = request.form['content']
    comment = Comment(content, session['user_id'], id)
    db.session.add(comment)
    db.session.commit()
    return redirect(f"/post/{id}")


@app.route('/categories')
def categories():
    return render_template('categories.html')
