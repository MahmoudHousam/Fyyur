from datetime import datetime
from data_models import Show, Artist, Venue, db

def get_past_upcoming_shows(venue_id):
    now = datetime.now()
    past_shows = db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue_id,
        Show.start_time < now
    ).all()
    upcoming_shows = db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue_id,
        Show.start_time >= now
    ).all()

    past_shows_data = [{
        'artist_id': show.artist_id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.start_time.isoformat()
    } for show in past_shows]

    upcoming_shows_data = [{
        'artist_id': show.artist_id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.start_time.isoformat()
    } for show in upcoming_shows]

    return past_shows_data, upcoming_shows_data
