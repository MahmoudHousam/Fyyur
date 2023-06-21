#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import json
import babel
import logging
from forms import *
import dateutil.parser
from flask_wtf import Form
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import contains_eager
from logging import Formatter, FileHandler
from flask import Flask, render_template, request, Response, flash, redirect, url_for
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(250))
    genres = db.Column(db.ARRAY(db.String(120)))
    seeking_description = db.Column(db.String(120))
    looking_for_talent = db.Column(db.Boolean)
    shows = db.relationship("Show", backref="venue", lazy=True)
    
    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'
      
      
      
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(250))
    genres = db.Column(db.ARRAY(db.String(120)))
    seeking_description = db.Column(db.String(120))
    looking_for_venue = db.Column(db.Boolean)
    shows = db.relationship("Show", backref="artist", lazy=True)
    
    def __repr__(self):
      return f'<Artist {self.id} {self.name}>'
      
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = "show"
  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)
  
  def __repr__(self) -> str:
     return f"<Show: {self.id}>"

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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venue = Venue
  show = Show
  locations = venue.query.order_by(venue.city, venue.state).all()
  data = []
  for location in locations:
    location_venues = venue.query.filter_by(state=location.city).filter_by(state=location.state).all()
    data.append(
      {
      "city": location.city,
      "state": location.state,
      "venues": [{
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(
          db.session.query(show).filter(show.venue_id == venue.id).filter(show.start_time > datetime.now()).all()
        )
      }
      for venue in location_venues
      ]
      }
    )
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  venue_results = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
  data = [
    {
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows":
          len(db.session.query(Show).filter(Show.venue_id == venue.id).
              filter(Show.start_time > datetime.now()).all())
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
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)

  upcoming = db.session.query(Show).join(Artist).filter(
    Show.venue_id == venue_id
  ).filter(
    Show.start_time <= datetime.now()
  ).all()
  
  past = db.session.query(Show).join(Artist).filter(
    Show.venue_id == venue_id
  ).filter(
    Show.start_time > datetime.now()
  ).all()

  upcoming_shows = [
    {
        'artist_id': show.artist_id,
        'artist_name': show.name,
        'artist_image_link': show.image_link,
        'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    for show in upcoming
  ]
  past_shows = [
    {
        'artist_id': show.artist_id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    for show in past
  ]

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
      'past_shows': past_shows,
      'upcoming_shows': upcoming_shows,
      'past_shows_count': len(past_shows),
      'upcoming_shows_count': len(upcoming_shows),
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
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
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
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
  # TODO: replace with real data returned from querying the database
  artist = Artist
  data = db.session.query(artist.id, artist.name).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get("search_term", "")
  artists_search = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  data = [
    {
      "id": artist.id,
      "name": artist.name,
      "num_upcomming_shows": len(db.session.query(Show).filter(Show.venue_id == artist.id).
              filter(Show.start_time > datetime.now()).all()),
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
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  past_shows = db.session.query(Show).join(Venue).filter(
    Show.artist_id == artist_id
  ).filter(
    Show.start_time < datetime.now()
  ).all()
  
  upcoming_shows = db.session.query(Show).join(Venue).filter(
    Show.artist_id == artist_id
  ).filter(
    Show.start_time >= datetime.now()
  ).all()
  
  past_show_lst = [
    {
      "venue_id": past_show.id,
      "venue_name": past_show.name,
      "venue_image_link": past_show.image_link,
      "start_time": past_show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    for past_show in past_shows 
  ]
  
  upcoming_show_lst = [
    {
      "venue_id": upcoming_show.id,
      "venue_name": upcoming_show.name,
      "venue_image_link": upcoming_show.image_link,
      "start_time": upcoming_show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    for upcoming_show in upcoming_shows 
  ]
  
  
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
    "past_shows": past_show_lst,
    "upcoming_shows": upcoming_show_lst,
    "past_shows_count": len(past_show_lst),
    "upcoming_shows_count": len(upcoming_show_lst),
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
  form.image_link.data = artist.image_link
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
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
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
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
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
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
          # TODO: on unsuccessful db insert, flash an error instead.
      else:
          flash('Artist ' + request.form['name'] + ' was successfully listed!')
  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
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
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
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
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
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
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
