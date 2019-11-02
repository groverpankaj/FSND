from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# ------------------------------------------------------------------------ #
# App Config.
# ------------------------------------------------------------------------ #

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)


# ------------------------------------------------------------------------ #
# Models.
# ------------------------------------------------------------------------ #


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String)
    venue_shows = db.relationship('Shows', backref='venues', lazy=True)

    def __repr__(self):
        return f'<id: {self.id}, name: {self.name}, genres: {self.genres}, city: {self.city}, state: {self.state}, address: {self.address}, phone: {self.phone}, website: {self.website}, facebook_link: {self.facebook_link}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(db.ARRAY(db.String))
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    artist_shows = db.relationship('Shows', backref='artists', lazy=True)
    artist_date_begin = db.Column(db.Date)
    artist_date_end = db.Column(db.Date)
    artist_time_begin = db.Column(db.Time)
    artist_time_end = db.Column(db.Time)

    def __repr__(self):
        return f'<id: {self.id}, name: {self.name}, genres: {self.genres}, city: {self.city}, state: {self.state}, phone: {self.phone}, website: {self.website}, facebook_link: {self.facebook_link}>'


class Shows(db.Model):
    __tablename__ = 'Shows'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime(timezone=True), nullable=False)

    def __repr__(self):
        return f'<id: {self.id}, venue_id: {self.venue_id}, artist_id: {self.artist_id}, start_time: {self.start_time}>'

