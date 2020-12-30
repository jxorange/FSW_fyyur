from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String(120)))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Venue', lazy=True)

    @property
    def upcoming_shows(self):
        upcoming_shows = [show for show in self.shows if
                          show.start_time > datetime.now()]
        return upcoming_shows

    @property
    def num_upcoming_shows(self):
        return len(self.upcoming_shows)

    @property
    def past_shows(self):
        past_shows = [show for show in self.shows if show.start_time < datetime.now()]
        return past_shows

    @property
    def num_past_shows(self):
        return len(self.past_shows)

    # implement any missing fields, as a database migration using Flask-Migrate     √


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Artist', lazy=True)

    @property
    def upcoming_shows(self):
        upcoming_shows = [show for show in self.shows if show.start_time > datetime.now()]
        return upcoming_shows

    @property
    def num_upcoming_shows(self):
        return len(self.upcoming_shows)

    @property
    def past_shows(self):
        past_shows = [show for show in self.shows if show.start_time < datetime.now()]

        return past_shows

    @property
    def num_past_shows(self):
        return len(self.past_shows)


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

    #  implement any missing fields, as a database migration using Flask-Migrate √

#  Implement Show and Artist models, and complete all model relationships and properties, as a database migration.  √
