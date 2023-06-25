#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import babel
import logging
from forms import *
import dateutil.parser
from flask_migrate import Migrate
from logging import Formatter, FileHandler
from helpers import get_past_upcoming_shows
from data_models import Artist, Venue, Show, app, db
from flask import render_template, request, flash, redirect, url_for


migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, dt_format='medium'):
  date = dateutil.parser.parse(value)
  if dt_format == 'full':
      dt_format="EEEE MMMM, d, y 'at' h:mma"
  elif dt_format == 'medium':
      dt_format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, dt_format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  locations = Venue.query.distinct(Venue.city, Venue.state).order_by(Venue.state, Venue.city).all()
  data = []
  for location in locations:
      location_data = {
          'city': location.city,
          'state': location.state,
          'venues': []
      }
      venues = Venue.query.filter_by(city=location.city, state=location.state).all()
      for venue in venues:
          num_upcoming_shows = Show.query.filter_by(venue_id=venue.id).filter(Show.start_time > datetime.now()).count()
          location_data['venues'].append({
              'id': venue.id,
              'name': venue.name,
              'num_upcoming_shows': num_upcoming_shows
          })
      data.append(location_data)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  venue_results = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
  data = [
    {
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": (
        Show.query.filter_by(venue_id=venue.id)
        .filter(Show.start_time > datetime.now())
        .count()
      ),
    }
    for venue in venue_results
  ]
  response = {
      "count": len(venue_results),
      "data": data,

  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  now = datetime.now()
  past_shows = db.session.query(Show).join(Artist).filter(
      Show.venue_id == venue_id,
      Show.start_time < now
  ).all()
  
  upcoming_shows = db.session.query(Show).join(Artist).filter(
      Show.venue_id == venue_id,
      Show.start_time >= now
  ).all()
  past_shows_ls = [
        {
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            'start_time': show.start_time.isoformat()
        }
        for show in past_shows
    ]
  
  upcoming_shows_ls = [
        {
            "artist_id": show.artist_is,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            'start_time': show.start_time.isoformat()
        }
        for show in upcoming_shows
    ]
  # past_shows, upcoming_shows = get_past_upcoming_shows(venue_id, "venue")
  datetime

  data = {
      'id': venue.id,
      'name': venue.name,
      'genres': venue.genres,
      'address': venue.address,
      'city': venue.city,
      'state': venue.state,
      'phone': venue.phone,
      'website': venue.website_link,
      'facebook_link': venue.facebook_link,
      'looking_for_talent': venue.looking_for_talent,
      'seeking_description': venue.seeking_description,
      'image_link': venue.image_link,
      'past_shows': past_shows_ls,
      'upcoming_shows': upcoming_shows_ls,
      'past_shows_count': len(past_shows_ls),
      'upcoming_shows_count': len(upcoming_shows_ls),
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  try:
      venue = Venue()
      venue.name = request.form['name']
      venue.city = request.form['city']
      venue.state = request.form['state']
      venue.address = request.form['address']
      venue.phone = request.form['phone']
      venue.genres = request.form.getlist('genres')
      venue.facebook_link = request.form['facebook_link']

      db.session.add(venue)
      db.session.commit()

  except Exception:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
      if error:
          flash('An error occurred: Venue ' + request.form['name'] + ' could not be listed')
      else:
          flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  try:
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
  except Exception:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
      if error:
          flash('An error occurred: Venue ' + request.form['name'] + ' could not be deleted')
      else:
          flash('Venue ' + request.form['name'] + ' was successfully deleted!')

  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artist = Artist
  data = db.session.query(artist.id, artist.name).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get("search_term", "")
  artists_search = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  query = """
          select id, name
          from public.'Artist'
          where name like '%{search_item}%'
          """
  # engine = create_engine()
  data = [
    {
      "id": artist.id,
      "name": artist.name,
      "num_upcomming_shows": (
        Show.query.filter_by(venue_id=artist.id)
        .filter(Show.start_time > datetime.now())
        .count()
      ),
    }
    for artist in artists_search
  ]
  response = {
    "count": len(artists_search),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  now = datetime.now()
  past_shows = db.session.query(Show).join(Artist).filter(
      Show.venue_id == artist_id,
      Show.start_time < now
  ).all()
  
  upcoming_shows = db.session.query(Show).join(Artist).filter(
      Show.venue_id == artist_id,
      Show.start_time >= now
  ).all()
  past_shows = [
        {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            'start_time': show.start_time.isoformat()
        }
        for show in past_shows
    ]
  
  upcoming_shows = [
        {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            'start_time': show.start_time.isoformat()
        }
        for show in upcoming_shows
    ]
  # past_shows, upcoming_shows = get_past_upcoming_shows(artist_id, "artist")
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "looking_for_venue": artist.looking_for_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  
  form.name.data = artist.name
  form.genres.data = artist.genres
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.website_link.data = artist.website_link
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.looking_for_venue or False
  form.seeking_description.data = artist.seeking_description
  form.image_link.data = artist.image_linkith
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  
  try:
    artist = db.session.query(Artist).get(artist_id)
    artist.name = request.form["name"]
    artist.genres = request.form.getlist('genres')
    artist.city = request.form["city"]
    artist.state = request.form["state"]
    artist.phone = request.form["phone"]
    artist.website_link = request.form["website_link"]
    artist.facebook_link = request.form["facebook_link"]
    artist.seeking_description = request.form["seeking_description"]
    artist.looking_for_venue = "seeking_venue" in request.form
    artist.image_link = request.form["image_link"]
    
    db.session.add(artist)
    db.session.commit()
  except Exception:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('An error occurred: Artist ' + request.form['name'] + ' could not be listed')
    else:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  
  form.name.data = venue.name
  form.genres.data = venue.genres
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.website_link.data = venue.website_link
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.looking_for_talent or False
  form.seeking_description.data = venue.seeking_description
  form.image_link.data = venue.image_link
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  
  try:
    venue = db.session.query(Venue).get(venue_id)
    venue.name = request.form["name"]
    venue.genres = request.form.getlist('genres')
    venue.city = request.form["city"]
    venue.state = request.form["state"]
    venue.phone = request.form["phone"]
    venue.website_link = request.form["website_link"]
    venue.facebook_link = request.form["facebook_link"]
    venue.seeking_description = request.form["seeking_description"]
    venue.looking_for_talent = "seeking_talent" in request.form
    venue.image_link = request.form["image_link"]
    
    db.session.add(venue)
    db.session.commit()
  except Exception:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('An error occurred: Venue ' + request.form['name'] + ' could not be listed')
    else:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return redirect(url_for('show_artist', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  try:
      artist = Artist()
      artist.name = request.form["name"]
      artist.city = request.form["city"]
      artist.state = request.form["state"]
      artist.phone = request.form["phone"]
      artist.genres = request.form.getlist("genres")
      artist.facebook_link = request.form["facebook_link"]
      artist.image_link = request.form["image_link"],
      artist.looking_for_venue = "seeking_venue" in request.form,
      artist.seeking_description=request.form["seeking_description"]

      db.session.add(artist)
      db.session.commit()

  except Exception:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
      if error:
          flash('An error occurred: Artist ' + request.form['name'] + ' could not be listed')
      else:
          flash('Artist ' + request.form['name'] + ' was successfully listed!')
  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = (
    db.session
    .query(Show)
    .join(Artist)
    .join(Venue)
    .all()
)
  
  data = [
    {
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.isoformat()
    }
    for show in shows
  ]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    try:
        show = Show(
            artist_id=request.form['artist_id'],
            venue_id=request.form['venue_id'],
            start_time=request.form['start_time']
        )

        db.session.add(show)
        db.session.commit()
    except Exception:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Show could not be listed.')
        else:
            flash('Show was successfully listed.')

    # on successful db insert, flash success
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

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

