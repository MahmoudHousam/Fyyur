import sys
import seeds
from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from app import Venue, Artist, Show

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
app.app_context().push()

venues = [
    dict(
        id=1,
        name="The Musical Hop",
        genres=["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        address="1015 Folsom Street",
        city="San Francisco",
        state="CA",
        phone="123-123-1234",
        website_link="https://www.themusicalhop.com",
        facebook_link="https://www.facebook.com/TheMusicalHop",
        looking_for_talent=True,
        seeking_description="We are on the lookout for a local artist to play every two weeks. Please call us.",
        image_link="https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    ),
    dict(
        id=2,
        name="Park Square Live Music & Coffee",
        genres=["ROCK N ROLL", "JAZZ", "CLASSICAL", "FOLK"],
        address="1015 Folsom Street",
        city="San Francisco",
        state="CA",
        phone="415-000-1234",
        website_link="https://www.parksquarelivemusicandcoffee.com",
        facebook_link="https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
        looking_for_talent=False,
        seeking_description="",
        image_link="https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80"
    ),
    dict(
        id=3,
        name="THE DUELING PIANOS BAR",
        genres=["CLASSICAL", "R&B", "HIP-HOP"],
        address="335 Delancey Street",
        city="New York",
        state="NY",
        phone="914-003-1132",
        website_link="https://www.theduelingpianos.com",
        facebook_link="https://www.facebook.com/theduelingpianos",
        looking_for_talent=False,
        seeking_description="",
        image_link="https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80"
    )
]
artists = [
    dict(
        id = 1,
        name = "GUNS N PETALS",
        city = "San Francisco",
        state = "CA",
        phone = "326-123-5000",
        image_link = "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        facebook_link = "https://www.facebook.com/GunsNPetals",
        website_link = "https://www.gunsnpetalsband.com",
        genres = ["ROCK N ROLL"],
        seeking_description = "Looking for shows to perform at in the San Francisco Bay Area!",
        looking_for_venue = True,
    ),
    dict(
        id = 2,
        name = "THE WILD SAX BAND",
        city = "San Francisco",
        state = "CA",
        phone = "432-325-5432",
        image_link = "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        facebook_link = "",
        website_link = "",
        genres = ["JAZZ", "CLASSICAL"],
        seeking_description = "",
        looking_for_venue = False,
    ),
    dict(
        id = 3,
        name = "MATT QUEVEDO",
        city = "New York",
        state = "NY",
        phone = "300-400-5000",
        image_link = "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        facebook_link = "https://www.facebook.com/mattquevedo923251523",
        website_link = "",
        genres = ["JAZZ"],
        seeking_description = "",
        looking_for_venue = False,
    )
]

# with app.app_context():
#     db.create_all()

def push_data(model, data):
    error = False
    try:
        for dict in data:
            art = model(**dict)
            db.session.add(art)
            db.session.commit()
    except Exception:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

push_data(Venue, venues)
push_data(Artist, artists)