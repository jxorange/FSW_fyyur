# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from flask_migrate import Migrate
from models import db, Venue, Artist, Show


from forms import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html', data=Artist.query.all())


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    #  replace with real venues data. num_shows should be aggregated based on number of upcoming shows per venue.  √
    data = []

    locations = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()
    for location in locations:
        venues = Venue.query.filter_by(city=location[0], state=location[1]).all()
        shows = venues[0].upcoming_shows

        data.append({
            "city": location[0],
            "state": location[1],
            "venues": venues + shows
        })

    return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
    #  implement search on artists with partial string search. Ensure it is case-insensitive.  √
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    search = '%' + request.form.get('search_term') + '%'
    venues = Venue.query.order_by(Venue.name).filter(Venue.name.ilike(search)).all()
    data = []

    for venue in venues:
        data.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": venue.num_upcoming_shows
        })
    count = len(data)

    response = {
        "count": count,
        "data": data
    }
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    try:
        data = []
        #  replace with real venue data from the venues table, using venue_id   √

        venue = Venue.query.get(venue_id)
        if venue:
            data = {
                "id": venue.id,
                "name": venue.name,
                "genres": venue.genres,
                "address": venue.address,
                "city": venue.city,
                "state": venue.state,
                "phone": venue.phone,
                "website": venue.website,
                "facebook_link": venue.facebook_link,
                "seeking_talent": True if venue.seeking_talent in (True, 't', 'True') else False,
                "seeking_description": venue.seeking_description,
                "image_link": venue.image_link if venue.image_link else "",
                "past_shows_count": venue.num_past_shows,
                "upcoming_shows_count": venue.num_upcoming_shows,
            }

        upcoming_shows = []
        for show in venue.upcoming_shows:
            artist = Artist.query.get(show.artist_id)
            upcoming_shows.append({
                "artist_id": show.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time)
            })
        past_shows = []
        for show in venue.past_shows:
            artist = Artist.query.get(show.artist_id)
            past_shows.append({
                "artist_id": show.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time)
            })

        data["upcoming_shows"] = upcoming_shows
        data["past_shows"] = past_shows

    except Exception as e:
        return e

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    #  insert form data as a new Venue record in the db, instead   √
    #  modify data to be the data object returned from db insertion   √

    form = VenueForm(request.form)
    try:
        venue = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            genres=form.genres.data,
            website=form.website.data,
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data
        )
        db.session.add(venue)

        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

    except Exception as e:
        db.session.rollback()
        print("eerere", e)
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

    finally:
        db.session.close()

    #  on unsuccessful db insert, flash an error instead.  √
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    #  Complete this endpoint for taking a venue_id, and using  √

    venue = Venue.query.get(venue_id)
    try:
        db.session.delete(venue)
        db.session.commit()
        flash('Venue ' + venue.name + ' was successfully deleted!')

    except Exception:
        db.session.rollback()
        flash('An error occurred. Venue ' + venue.name + ' could not be deleted.')

    finally:
        db.session.close()
    # returns the name of
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    #  replace with real data returned from querying the database    √
    artists = Artist.query.with_entities(Artist.id, Artist.name).all()

    data = []
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    #  implement search on artists with partial string search. Ensure it is case-insensitive.   √
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search = '%' + request.form.get('search_term') + '%'
    artists = Artist.query.order_by(Artist.name).filter(Artist.name.ilike(search)).all()
    data = []

    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": artist.num_upcoming_shows
        })
    count = len(data)

    response = {
        "count": count,
        "data": data
    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    #  replace with real venue data from the venues table, using venue_id    √
    try:
        data = []
        artist = Artist.query.get(artist_id)

        if artist:
            data = {
                "id": artist.id,
                "name": artist.name,
                "genres": artist.genres,
                "city": artist.city,
                "state": artist.state,
                "phone": artist.phone,
                "website": artist.website,
                "facebook_link": artist.facebook_link,
                "seeking_venue": True if artist.seeking_venue in (True, 't', 'True') else False,
                "seeking_description": artist.seeking_description,
                "image_link": artist.image_link,
                "past_shows_count": artist.num_past_shows,
                "upcoming_shows_count": artist.num_upcoming_shows,
            }

        upcoming_shows = []
        for show in artist.upcoming_shows:
            venue = Venue.query.get(show.venue_id)
            upcoming_shows.append({
                "venue_id": venue.id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": str(show.start_time)
            })

        past_shows = []
        for show in artist.past_shows:
            venue = Venue.query.get(show.venue_id)
            past_shows.append({
                "venue_id": venue.id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": str(show.start_time)
            })

        data["upcoming_shows"] = upcoming_shows
        data["past_shows"] = past_shows


    except Exception as e:
        return e
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    try:
        artist = Artist.query.get(artist_id)

        form = ArtistForm(
            name=artist.name,
            genres=[i for i in artist.genres],
            city=artist.city,
            state=artist.state,
            phone=artist.phone,
            website=artist.website,
            facebook_link=artist.facebook_link,
            seeking_venue=artist.seeking_venue,
            seeking_description=artist.seeking_description,
            image_link=artist.image_link
        )
    except Exception as e:
        return e
    # populate form with fields from artist with ID <artist_id>     √
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # take values from the form submitted, and update existing   √

    artist = Artist.query.get(artist_id)
    try:
        artist.name = request.form.get('name')
        artist.city = request.form.get('city')
        artist.state = request.form.get('state')
        artist.phone = request.form.get('phone')
        artist.genres = request.form.getlist('genres')
        artist.website = request.form.get('website')
        artist.facebook_link = request.form.get('facebook_link')
        artist.image_link = request.form.get('image_link')
        artist.seeking_venue = True if request.form.get('seeking_venue') == 'y' else False
        artist.seeking_description = request.form.get('seeking_description')

        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully updated!')

    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')

    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)

    form = VenueForm(
        name=venue.name,
        genres=[i for i in venue.genres],
        address=venue.address,
        city=venue.city,
        state=venue.state,
        phone=venue.phone,
        website=venue.website,
        facebook_link=venue.facebook_link,
        seeking_talent=venue.seeking_talent,
        seeking_description=venue.seeking_description,
        image_link=venue.image_link
    )

    #  populate form with values from venue with ID <venue_id>    √
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    #  take values from the form submitted, and update existing  √
    venue = Venue.query.get(venue_id)
    try:
        venue.name = request.form.get('name')
        venue.city = request.form.get('city')
        venue.state = request.form.get('state')
        venue.address = request.form.get('address')
        venue.phone = request.form.get('phone')
        venue.genres = request.form.getlist('genres')
        venue.website = request.form.get('website')
        venue.facebook_link = request.form.get('facebook_link')
        venue.image_link = request.form.get('image_link')
        venue.seeking_talent = True if request.form.get('seeking_talent') == 'y' else False
        venue.seeking_description = request.form.get('seeking_description')

        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully updated!')

    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')

    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    #  insert form data as a new Venue record in the db, instead     √
    #  modify data to be the data object returned from db insertion      √

    form = ArtistForm(request.form)
    try:
        artist = Artist(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            genres=form.genres.data,
            website=form.website.data,
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            seeking_venue=form.seeking_venue.data,
            seeking_description=form.seeking_description.data
        )
        db.session.add(artist)

        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

    finally:
        db.session.close()

    #  on unsuccessful db insert, flash an error instead.     √
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    #  replace with real venues data. num_shows should be aggregated based on number of upcoming shows per venue.     √
    data = []

    shows = Show.query.join(Venue, (Venue.id == Show.venue_id)).join(Artist, (Artist.id == Show.artist_id)) \
        .with_entities(Show.venue_id, Venue.name.label('venue_name'), Show.artist_id, Artist.name.label('artist_name'),
                       Artist.image_link, Show.start_time)
    for show in shows:
        data.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue_name,
            "artist_id": show.artist_id,
            "artist_name": show.artist_name,
            "artist_image_link": show.image_link,
            "start_time": str(show.start_time)
        })
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # insert form data as a new Show record in the db, instead   √

    try:
        show = Show(
            venue_id=request.form.get('venue_id'),
            artist_id=request.form.get('artist_id'),
            start_time=request.form.get('start_time')
        )
        db.session.add(show)

        db.session.commit()
        flash('Show was successfully listed!')

    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')

    finally:
        db.session.close()
    #  on unsuccessful db insert, flash an error instead. √

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def server_error(error):
    return render_template('errors/500.html'), 403

@app.errorhandler(405)
def server_error(error):
    return render_template('errors/500.html'), 405


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
