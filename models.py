from flask_app import Flask, db, flash, EMAIL_REGEX, session, datetime


favorites = db.Table(
    'favorites',
    db.Column('user_id', db.Integer, db.ForeignKey(
        'users.id')),
    db.Column('movie_id', db.Integer, db.ForeignKey(
        'movies.id'))
)


post_likes = db.Table(
    'post_likes',
    db.Column('user_id', db.Integer, db.ForeignKey(
        'users.id')),
    db.Column('post_id', db.Integer, db.ForeignKey(
        'posts.id'))
)


comment_likes = db.Table(
    'comment_likes',
    db.Column('user_id', db.Integer, db.ForeignKey(
        'users.id'), primary_key=True),
    db.Column('comment_id', db.Integer, db.ForeignKey(
        'comments.id'), primary_key=True)
)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True,
                   nullable=False)
    username = db.Column(db.String(45), unique=True)
    password = db.Column(db.String(255))
    email = db.Column(db.String(45), unique=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    favorites = db.relationship(
        'Movie', secondary=favorites, backref='favorites')

    def __init__(self, username, password, email, first_name, last_name):
        self.username = username
        self.password = password
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

    def __repr__(self):
        return f"User {self.username}"

    @staticmethod
    def validate_user(user: dict) -> bool:
        is_valid = True
        # ensures proper length
        if len(user['first_name']) < 3:
            is_valid = False
            flash('Name must be at least 3 characters', 'first_name')
        if len(user['last_name']) < 3:
            is_valid = False
            flash('Name must be at least 3 characters.', 'last_name')
        # disallows numerals in first/last name
        if any(c.isnumeric() for c in user['first_name']):
            is_valid = False
            flash('Numbers not allowed.', 'first_name')
        if any(c.isnumeric() for c in user['last_name']):
            is_valid = False
            flash('Numbers not allowed.', 'last_name')
        if not EMAIL_REGEX.match(user['email']):
            is_valid = False
            flash('Invalid email address.', 'email')
        email_in_db = User.query.filter_by(email=user['email']).first()
        if email_in_db:
            is_valid = False
            flash('Email is already in use. Try using it to log in.', 'email')
        user_in_db = User.query.filter_by(username=user['username']).first()
        if user_in_db:
            is_valid = False
            flash('Username is already in use. Try using it to log in.', 'username')
        if 'password_confirmation' in user:
            if user['password'] != user['password_confirmation']:
                is_valid = False
                flash('Passwords must match.', 'password')
            if len(user['password']) < 8:
                is_valid = False
                flash('Password must be at least 8 characters.', 'password')
        return is_valid


class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column('id', db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(1024))
    year = db.Column(db.Integer, nullable=False)
    mpaa_rating = db.Column(db.String(32))
    genre = db.Column(db.String(255))
    imdb_id = db.Column(db.String(45))
    tmdb_id = db.Column(db.Integer)
    poster_path = db.Column(db.String(255))

    def __init__(self, title, description, year, mpaa_rating, genre, imdb_id, tmdb_id, poster_path):
        self.title = title
        self.description = description
        self.year = year
        self.mpaa_rating = mpaa_rating
        self.genre = genre
        self.imdb_id = imdb_id
        self.tmdb_id = tmdb_id
        self.poster_path = poster_path


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column('id', db.Integer, primary_key=True)
    type = db.Column(db.String(64))
    title = db.Column(db.String(64))
    content = db.Column(db.String(16384))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'))
    created_at = db.Column(db.DateTime)

    def __init__(self, type, title, content, user_id, movie_id, created_at=datetime.datetime.now()):
        self.type = type
        self.title = title
        self.content = content
        self.user_id = user_id
        self.movie_id = movie_id
        self.created_at = created_at

    @staticmethod
    def validate_post(post: dict) -> bool:
        is_valid = True
        if len(post['content']) < 32:
            is_valid = False
            flash("That's too short for a post. Have fun with this!")
        if len(post['title']) < 3:
            is_valid = False
            flash("Title must be at least 3 characters.")
        return is_valid


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column('id', db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    created_at = db.Column(db.DateTime)

    def __init__(self, content, user_id, post_id, created_at=datetime.datetime.now()):
        self.content = content
        self.user_id = user_id
        self.post_id = post_id
        self.created_at = created_at


def faved(tmdb_id):
    faved = False
    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()
        movie = Movie.query.filter_by(tmdb_id=tmdb_id).first()
        faved = movie in user.favorites
    return faved
