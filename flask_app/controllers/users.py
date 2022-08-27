from flask_app import app, db, render_template, request, redirect, bcrypt, session, flash, url_for, EMAIL_REGEX, verify_logged_in, datetime, timedelta
from models import User, Movie, Post, Comment, favorites, post_likes, comment_likes, faved


@app.route('/')
def index():
    upms = db.session.query(User, Post, Movie).select_from(User).join(
        Post).join(Movie).where(Post.user_id == User.id and Post.movie_id == Movie.id).order_by(Post.created_at.desc()).all()
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
        session['firt_name'] = user.first_name
        session['user_id'] = user.id
        session['username'] = user.username
        print(
            f"Logged in {session['first_name']} with ID {session['user_id']}")
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
        session['first_name'] = user_in_db.first_name
        session['user_id'] = user_in_db.id
        session['username'] = user_in_db.username
        print(
            f"Logged in {session['username']} ({session['first_name']})")
        return redirect(request.form['last_route'])
    else:
        return render_template('login.html', last_route=request.referrer)


@app.route('/logout')
def logout():
    print(f"Logged out {session['username']} ({session['first_name']})")
    session.pop('user_id', None)
    session.pop('first_name', None)
    session.pop('username', None)
    return redirect(request.referrer)
