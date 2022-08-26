from flask_app import app, db, render_template, request, redirect, bcrypt, session, flash, url_for, EMAIL_REGEX, verify_logged_in
from models import User, Movie, Post, Comment, favorites, post_likes, comment_likes, faved
# from flask_app.models.movie import Movie
# from flask_app.models.post import Post
# from flask_app.models.comment import Comment


@app.route('/')
def index():
    posts = Post.query.all()
    upms = db.session.query(User, Post, Movie).select_from(User).join(
        Post).join(Movie).where(Post.user_id == User.id and Post.movie_id == Movie.id).all()
    return render_template('feed.html', upms=upms, truncate=True, title='Main Feed | ReDirector')


@app.route('/registration', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        if not User.validate_user(request.form):
            return redirect('/registration')
        user = User(
            request.form['username'],
            bcrypt.generate_password_hash(request.form['password']),
            request.form['email'],
            request.form['first_name'],
            request.form['last_name']
        )
        db.session.add(user)
        db.session.commit()
        user = User.query.filter_by(
            email=request.form['email']).first()
        session['user'] = user.first_name
        session['user_id'] = user.id
        print(
            f"Logged in {session['user']} with ID {session['user_id']}")
        return redirect('/')
    else:
        return render_template('registration.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        # check if user used email to login
        if EMAIL_REGEX.match(request.form['username_email']):
            # check if email is in database
            user_in_db = User.query.filter_by(
                email=request.form['username_email']).first()
        else:
            # check if username is in database
            user_in_db = User.query.filter_by(
                username=request.form['username_email']).first()
        if not user_in_db:
            flash('Invalid Username/Email', 'username_email')
            return redirect('/login')
        # check password against stored hash
        if not bcrypt.check_password_hash(user_in_db.password, request.form['log_password']):
            flash('Invalid Password', 'log_password')
            return redirect('/login')
        # email and password are valid
        session['user'] = user_in_db.first_name
        session['user_id'] = user_in_db.id
        print(
            f"Logged in {session['user']} with ID {session['user_id']}")
        return redirect(request.form['last_route'])
    else:
        return render_template('login.html', last_route=request.referrer)


@app.route('/logout')
def logout():
    print(f"Logging out {session['user']}")
    session.pop('user_id', None)
    session.pop('user', None)
    return redirect(request.referrer)