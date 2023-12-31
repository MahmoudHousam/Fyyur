#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)



#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(250), nullable=True)
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    seeking_description = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean)
    shows = db.relationship("Show", backref="venue", lazy=True)
    
    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'
      
      
      
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(250), nullable=True)
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    seeking_description = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean)
    shows = db.relationship("Show", backref="artist", lazy=True)
    
    def __repr__(self):
      return f'<Artist {self.id} {self.name}>'
      
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = "Show"
  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)
  
  def __repr__(self) -> str:
     return f"<Show: {self.id}>"
