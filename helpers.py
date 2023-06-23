from datetime import datetime
from data_models import Show, Artist, Venue, db

def get_past_upcoming_shows(venue_id, page):
    now = datetime.now()
    past_shows = db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue_id,
        Show.start_time < now
    ).all()
    
    upcoming_shows = db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue_id,
        Show.start_time >= now
    ).all()
    def show_data(show_time):
        show = [
            {
                "artist_id" if page=="artist" else "venue_id":
                    show.artist_id if page=="artist" else show.venue_id,
                "artist_name" if page=="artist" else "venue_name":
                    show.artist.name if page=="artist" else show.venue.name,
                "artist_image_link" if page=="artist" else "venue_image_link":
                    show.artist.image_link if page=="artist" else show.venue.image_link,
                'start_time': show.start_time.isoformat()
            }
            for show in show_time
        ]
        return show
    
    past_shows_data = show_data(past_shows)
    upcoming_shows_data = show_data(upcoming_shows)

    return past_shows_data, upcoming_shows_data
