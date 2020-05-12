#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
import datetime, time

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI']= 'postgres://postgres:14231423az@localhost:5432/fyyur'
migrate = Migrate(app, db)


# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Shows(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    date = db.Column(db.String(), nullable=False)
    venues = db.relationship("Venue", back_populates="artists")
    artists = db.relationship("Artist", back_populates="venues")


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
    genres = db.Column(db.String(120))
    website = db.Column(db.String(), default="NO website")
    seeking_description = db.Column(db.String(), default="NO Description")
    seeking_talent = db.Column(db.Boolean, default=False)
    artists = db.relationship("Shows", back_populates="venues")


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(), default="NO website")
    seeking_description = db.Column(db.String(), default="NO Description")
    seeking_venue =  db.Column(db.Boolean, default=False)
    show = db.relationship('Shows')
    venues = db.relationship("Shows", back_populates="artists")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  dataSort = {}
  keys = []
  allVenues = Venue.query.all()
  for venue in allVenues:
    if venue.state in dataSort:
      if venue.city in dataSort[venue.state]:
         dataSort[venue.state][venue.city].append({"name":venue.name, "id":venue.id,"num_upcoming_shows":len(venue.artists)})
      else:
          keys.append({"state": venue.state, "city":venue.city})
          dataSort[venue.state][venue.city] = [{"name":venue.name, "id":venue.id,"num_upcoming_shows":len(venue.artists)}]
    else:
      keys.append({"state": venue.state, "city":venue.city})
      dataSort[venue.state] ={}
      dataSort[venue.state][venue.city] = [{"name":venue.name, "id":venue.id,"num_upcoming_shows":len(venue.artists)}]


  for key in keys:
    data.append({
       "city": key['city'],
        "state":key['state'],
        "venues":dataSort[key['state']][key['city']]

    })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  name = request.form.get('search_term', '')
  re = Venue.query.filter(Venue.name.like("%"+ request.form.get('search_term', '') +"%")).all()
  count = len(re)
  response={
    "count":count,
    "data": re
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  

  venue = Venue.query.get(venue_id)

  today = datetime.datetime.now().timetuple()
  todayInSeconds = time.mktime(today)

  def get_time(date):
    year = date[0]+date[1]+date[2]+date[3]
    month = date[5]+date[6]
    day = date[8]+date[9]
    hour = date[11]+date[12]
    menute = date[14]+date[15]
    sec = date[17]+date[18]
    showTiem =  datetime.datetime(int(year), int(month), int(day), int(hour), int(menute), int(sec)).timetuple()
    showTimeInSec= time.mktime(showTiem)
    return showTimeInSec

  def past_shows():
    past=[]
    for show in venue.artists:
      if get_time(show.date) < todayInSeconds:
        past.append({
          "artist_id":show.artists.id,
          "artist_name":show.artists.name,
          "artist_image_link":show.artists.image_link,
          "start_time":show.date,
          })
    return past

  def upcoming_shows():
    upcoming=[]
    for show in venue.artists:
      if get_time(show.date) > todayInSeconds:
        upcoming.append({
          "artist_id":show.artists.id,
          "artist_name":show.artists.name,
          "artist_image_link":show.artists.image_link,
          "start_time":show.date,
          })
    return upcoming

  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": 'change',
    "image_link": venue.image_link,
    "past_shows": past_shows(),
    "upcoming_shows": upcoming_shows(),
    "past_shows_count": len( past_shows()),
    "upcoming_shows_count": len( upcoming_shows()),
  }

  data = list(filter(lambda d: d['id'] == venue_id, [data]))[0]
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

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  try:
    venue = Venue(name = request.form['name'], city =request.form['city'], state = request.form['state'],
    address = request.form['address'], phone = request.form['phone'],
    facebook_link = request.form['facebook_link'], genres = request.form['genres'])
    db.session.add(venue)
    db.session.commit()
    venueNmae = Venue.query.filter_by(name= venue.name).first().name
  except:
      flash('Venue ' + request.form['name'] + ' could not be listed.')
      db.session.rollback()
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

  try:
    Venue.query.get(id=venue_id).delete()
    return True
  except:
    return None
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  try:
    artist = Artist.query.all()
    data=[]
    i=0
    for ar in artist:
      data.append({
        "id": artist[i].id,
        "name": artist[i].name,
      })
      i=i+1
    return render_template('pages/artists.html', artists=data)
  except:
    error = True
  finally:
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  name = request.form.get('search_term', '')
  re = Artist.query.filter(Artist.name.like("%"+ request.form.get('search_term', '') +"%")).all()
  count =  len(re)
  response={
    "count":count,
    "data": re
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  artist = Artist.query.get(artist_id)

  today = datetime.datetime.now().timetuple()
  todayInSeconds = time.mktime(today)

  def get_time(date):
    year = date[0]+date[1]+date[2]+date[3]
    month = date[5]+date[6]
    day = date[8]+date[9]
    hour = date[11]+date[12]
    menute = date[14]+date[15]
    sec = date[17]+date[18]
    showTiem =  datetime.datetime(int(year), int(month), int(day), int(hour), int(menute), int(sec)).timetuple()
    showTimeInSec= time.mktime(showTiem)
    return showTimeInSec

  def past_shows():
    past=[]
    for show in artist.venues:
      if get_time(show.date) < todayInSeconds:
        past.append({
          "artist_id":show.artists.id,
          "artist_name":show.artists.name,
          "artist_image_link":show.artists.image_link,
          "start_time":show.date,
          })
    return past

  def upcoming_shows():
    upcoming=[]
    for show in artist.venues:
      if get_time(show.date) > todayInSeconds:
        upcoming.append({
          "artist_id":show.artists.id,
          "artist_name":show.artists.name,
          "artist_image_link":show.artists.image_link,
          "start_time":show.date,
          })
    return upcoming

  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows(),
    "upcoming_shows": upcoming_shows(),
    "past_shows_count": len(past_shows()),
    "upcoming_shows_count": len(upcoming_shows()),
  }

  data = list(filter(lambda d: d['id'] == artist_id, [data]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  
  artist=Artist.query.get(artist_id)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)
  artist.name = request.form['name']
  artist.city = request.form['city']
  artist.state = request.form['state']
  artist.phone = request.form['phone']
  artist.genres = request.form['genres']
  artist.facebook_link = request.form['facebook_link']
  db.session.commit()
  db.session.close()


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  venue = Venue.query.get(venue_id)
  venue.name = request.form['name']
  venue.city = request.form['city']
  venue.state = request.form['state']
  venue.phone = request.form['phone']
  venue.genres = request.form['genres']
  venue.facebook_link = request.form['facebook_link']
  venue.address = request.form['address']
  db.session.commit()
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  try:
    artist = Artist(name = request.form['name'], city =request.form['city'], state = request.form['state'],
    phone = request.form['phone'], facebook_link = request.form['facebook_link'], genres = request.form['genres'])
    db.session.add(artist)
    db.session.commit()
    artistNmae = Artist.query.filter_by(name= artist.name).first().name
    flash('Artist ' + artistNmae + ' was successfully listed!')
  except:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      db.session.rollback()
      print(sys.exc_info())
  finally:
    db.session.close()

  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  allShows = Shows.query.all()

  data=[]

  for show in allShows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venues.name,
      "artist_id": show.artist_id,
      "artist_name": show.artists.name,
      "artist_image_link": show.artists.image_link,
      "start_time": show.date
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
  # TODO: insert form data as a new Show record in the db, instead
  # on successful db insert, flash success
  try:
    show = Shows(artist_id = request.form['artist_id'], venue_id= request.form['venue_id'], date = request.form['start_time'])
    artist = Artist.query.get(request.form['artist_id'])
    venue = Venue.query.get(request.form['venue_id'])
    show.venues = venue
    artist.venues.append(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    print(sys.exc_info())
    db.session.rollback()
    flash('Show was not successfully listed!')
  finally:
    db.session.close()

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
