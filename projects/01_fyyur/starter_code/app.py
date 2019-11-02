# -------------------------------------------------------------------------- #
# Imports
# -------------------------------------------------------------------------- #

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from werkzeug.datastructures import ImmutableMultiDict
from sqlalchemy import desc, func
from models import Artist, Venue, Shows, db, app, migrate


# ------------------------------------------------------------------------ #
# Filters.
# ------------------------------------------------------------------------ #

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

# ------------------------------------------------------------------------ #
# Controllers.
# ------------------------------------------------------------------------ #


@app.route('/')
def index():
    latest_venues = Venue.query.order_by(desc('id')).limit(10).all()
    latest_artists = Artist.query.order_by(desc('id')).limit(10).all()
    return render_template('pages/home.html', latest_venues=latest_venues, latest_artists=latest_artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

    all_cities = db.session.query(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
    # print(all_cities)
    data = []

    for each_city in all_cities:
        city_dict = {}
        city_dict['city'] = each_city.city
        city_dict['state'] = each_city.state

        venues_list = []
        all_venues_in_city = Venue.query.filter_by(city=each_city[0], state=each_city[1]).all()

        for each_venue in all_venues_in_city:
            venue_dict = {}
            venue_dict['id'] = each_venue.id
            venue_dict['name'] = each_venue.name

            all_shows_in_venue = each_venue.venue_shows  # backref

            upcoming = 0
            for each_show in all_shows_in_venue:

                if(each_show.start_time > datetime.now()):
                    upcoming += 1

            venue_dict['num_upcoming_shows'] = upcoming

            venues_list.append(venue_dict)  # each venue in a city

            city_dict['venues'] = venues_list  # all venues in a city

        data.append(city_dict)    # each city data appended

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():

    search_term = request.form.get('search_term', '')
    search = func.lower("%{}%".format(search_term))

    all_venues = Venue.query.filter(func.lower(Venue.name).like(search)).all()

    # print(all_venues)

    all_venue_data = []

    for each_venue in all_venues:

        shows_by_venue = each_venue.venue_shows

        upcoming_shows = 0

        for each_show in shows_by_venue:
            if(datetime.now() < each_show.start_time):
                upcoming_shows += 1

        venue_data = {}
        venue_data['id'] = each_venue.id
        venue_data['name'] = each_venue.name
        venue_data['num_upcoming_shows'] = upcoming_shows

        all_venue_data.append(venue_data)

    response = {}

    response['count'] = len(all_venue_data)
    response['data'] = all_venue_data

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

    data = Venue.query.filter_by(id=venue_id).first()

    shows_in_venue = data.venue_shows  # Calling child

    past_shows = []
    upcoming_shows = []

    for each_show in shows_in_venue:
        showdict = {
            "artist_id": each_show.artists.id,
            "artist_name": each_show.artists.name,
            "artist_image_link": each_show.artists.image_link,
            "start_time": each_show.start_time.strftime("%B %d, %Y %H:%M:%S")
        }

        if(datetime.now() < each_show.start_time):
                upcoming_shows.append(showdict)
        else:
                past_shows.append(showdict)

    data.past_shows = past_shows
    data.upcoming_shows = upcoming_shows

    data.past_shows_count = len(past_shows)
    data.upcoming_shows_count = len(upcoming_shows)

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

    data_recd_imm = request.form
    # print(data_recd_imm)

    just_fetch = Venue.query.first()   # if we skip this then id is None & error occurs

    venue_ins = Venue()        # Instance of class

    for i in data_recd_imm:
        if(i == 'genres'):
            setattr(venue_ins, i, data_recd_imm.getlist('genres'))   # As 'genres' key has multiple values
        else:
            setattr(venue_ins, i, data_recd_imm[i])

    # print(venue_ins)

    error = False

    try:
        db.session.add(venue_ins)   # Insert in DB
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()

    if(error):
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

    try:
        venueToDelete = Venue.query.filter_by(id=venue_id)   # Delete  DB
        # print(venueToDelete)
        venueToDelete.delete()

        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return "Success"

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():

    data = Artist.query.order_by('name').all()

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():

    search_term = request.form.get('search_term', '')
    search = func.lower("%{}%".format(search_term))

    all_artists = Artist.query.filter(func.lower(Artist.name).like(search)).all()

    # print(all_artists)

    all_artists_data = []

    for each_artist in all_artists:

        shows_by_artist = each_artist.artist_shows

        upcoming_shows = 0

        for each_show in shows_by_artist:
            if(datetime.now() < each_show.start_time):
                upcoming_shows += 1

        artist_data = {}
        artist_data['id'] = each_artist.id
        artist_data['name'] = each_artist.name
        artist_data['num_upcoming_shows'] = upcoming_shows

        all_artists_data.append(artist_data)

    response = {}

    response['count'] = len(all_artists_data)
    response['data'] = all_artists_data

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

    data = Artist.query.filter_by(id=artist_id).first()
    # print(artist_id, ' : ', data)
    shows_by_artist = data.artist_shows

    past_shows = []
    upcoming_shows = []

    for each_show in shows_by_artist:
        showdict = {
            "venue_id": each_show.venues.id,
            "venue_name": each_show.venues.name,
            "venue_image_link": each_show.venues.image_link,
            "start_time": each_show.start_time.strftime("%B %d, %Y %H:%M:%S")
        }

        if(datetime.now() < each_show.start_time):
            upcoming_shows.append(showdict)
        else:
            past_shows.append(showdict)

    data.past_shows = past_shows
    data.upcoming_shows = upcoming_shows

    data.past_shows_count = len(past_shows)
    data.upcoming_shows_count = len(upcoming_shows)

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    artist = Artist.query.filter_by(id=artist_id).first()

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

    data_recd_imm = request.form
    # print(data_recd_imm)

    artist_ins = Artist.query.filter_by(id=artist_id).first()

    for i in data_recd_imm:
        if(i == 'genres'):
            setattr(artist_ins, i, data_recd_imm.getlist('genres'))   # As 'genres' key has multiple values
        else:
            setattr(artist_ins, i, data_recd_imm[i])

    # print(artist_ins)

    error = False

    try:
        db.session.commit()  # Edit DB
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()

    if(error):
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
    else:
        flash('Artist ' + request.form['name'] + ' was successfully edited!')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    venue = Venue.query.filter_by(id=venue_id).first()

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

    data_recd_imm = request.form
    # print(data_recd_imm)

    venue_ins = Venue.query.filter_by(id=venue_id).first()

    for i in data_recd_imm:
        if(i == 'genres'):
            setattr(venue_ins, i, data_recd_imm.getlist('genres'))   # As 'genres' key has multiple values
        else:
            setattr(venue_ins, i, data_recd_imm[i])

    # print(artist_ins)

    error = False

    try:
        db.session.commit()   # Edit DB
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()

    if(error):
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
    else:
        flash('Venue ' + request.form['name'] + ' was successfully edited!')
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

    data_recd_imm = request.form
    # print(data_recd_imm)

    just_fetch = Artist.query.first()  # if we skip this then id is None & error occurs

    artist_ins = Artist()        # Instance of class

    for i in data_recd_imm:
        if(i == 'genres'):
            setattr(artist_ins, i, data_recd_imm.getlist('genres'))   # As 'genres' key has multiple values
        else:
            setattr(artist_ins, i, data_recd_imm[i])

    # print(artist_ins)

    error = False

    try:
        db.session.add(artist_ins)  # Insert in DB
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()

    if(error):
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    else:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

    data = Shows.query.all()

    for each_show in data:
        each_show.venue_name = each_show.venues.name    # backref
        each_show.artist_name = each_show.artists.name
        each_show.artist_image_link = each_show.artists.image_link
        each_show.start_time = each_show.start_time.strftime("%B %d, %Y %H:%M:%S")  # Convert to String

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form

    data_recd_imm = request.form
    # print(data_recd_imm)

    just_fetch = Shows.query.first()  # if we skip this then id is None & error occurs

    show_ins = Shows()        # Instance of class

    for i in data_recd_imm:
        setattr(show_ins, i, data_recd_imm[i])

    show_ins.start_time = datetime.strptime(show_ins.start_time, '%Y-%m-%d %H:%M:%S')

    show_date = show_ins.start_time.date()
    show_time = show_ins.start_time.time()

    reqArtist = Artist.query.filter_by(id=show_ins.artist_id).first()

    timingNotSuitable = False  # Default state

    if ((reqArtist.artist_time_begin) and (show_time < reqArtist.artist_time_begin)):   # Check begin time
        timingNotSuitable = True
    if ((reqArtist.artist_time_end) and (show_time > reqArtist.artist_time_end)):   # Check end time
        timingNotSuitable = True
    if ((reqArtist.artist_date_begin) and (show_date < reqArtist.artist_date_begin)):  # Check begin time
        timingNotSuitable = True
    if ((reqArtist.artist_date_end) and (show_date > reqArtist.artist_date_end)):   # Check end time
        timingNotSuitable = True

    if(timingNotSuitable):
        flash('Available date for artist is ' + reqArtist.artist_date_begin.strftime('%Y-%m-%d') + ' to ' + reqArtist.artist_date_end.strftime('%Y-%m-%d') + ' between ' + reqArtist.artist_time_begin.strftime('%H:%M:%S') + ' to ' + reqArtist.artist_time_end.strftime('%H:%M:%S'))
        return redirect(url_for('create_shows'))

    error = False

    try:
        db.session.add(show_ins)  # Insert in DB
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()

    if(error):
        flash('An error occurred. Show could not be listed.')
    else:
        flash('Show was successfully listed!')

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ------------------------------------------------------------------------ #
# Launch.
# ------------------------------------------------------------------------ #

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
