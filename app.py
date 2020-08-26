#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

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
from datetime import datetime
import sys
from models import db, Venue, Artist, Shows
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://arueh:trumpet641@localhost:5432/project1'

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
  venues = Venue.query.all()
  data = []
  for venue in venues:
    city = venue.city
    state = venue.state
    specific_venues = Venue.query.filter_by(city=city, state=state).all()
    for specific_venue in specific_venues:
      id_of_specific_venue = specific_venue.id
      name_of_specific_venue = specific_venue.name
      number_of_shows_of_specific_venue = len(specific_venue.shows)
      obj = {
        'city': city,
        'state': state,
        'venues': [{
          'id': id_of_specific_venue,
          'name': name_of_specific_venue,
          'num_upcoming_shows': number_of_shows_of_specific_venue
        }]
      }
      data.append(obj)
  return render_template('pages/venues.html', areas=data)



@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()
  data = []
  for venue in venues:
    obj = {
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': len(venue.shows)
    }
    data.append(obj)

  response = {
    "count": len(venues),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  print('I am in area 1')
  venues = Venue.query.all()
  shows = Shows.query.all()
  past_shows = []
  upcoming_shows = []
  

  for show in shows:
    print('I am in area 2')
    current_date = datetime.now()
    show_date = date   
    if show_date > current_date:
      upcoming_shows.append(show)
    else: 
      past_shows.append(show)
  
  def find_past_shows(venueId):
    if past_shows:
      for past_show in past_shows:
        if past_show.venue_id == venueId:
            past_show_artist=Artist.query.get(past_show.artist_id)
            return [{ 'artist_id': past_show.artist_id, 'artist_name': past_show_artist.name, 'artist_image_link': past_show_artist.image_link, 'start_time': str(past_show.date) }]
        else:
          return []
    else: 
      return []

  def find_upcoming_shows(venueId):
    if upcoming_shows:
      for upcoming_show in upcoming_shows:
        if upcoming_show.venue_id == venueId:
            upcoming_show_artist = Artist.query.get(upcoming_show.artist_id)
            return [{'artist_id': upcoming_show.artist_id, 'artist_name': upcoming_show_artist.name, 'artist_image_link': upcoming_show_artist.image_link, 'start_time': str(upcoming_show.date)}]
        else:
          return[]
    else:
      return []

  venues_data = [] 
  for venue in venues:
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
      'seeking_talent': venue.seeking,
      'seeking_description': venue.seeking_description,
      'image_link': venue.image_link,
      'past_shows': find_past_shows(venue.id),
      'upcoming_shows': find_upcoming_shows(venue.id),
      'past_shows_count': len(find_past_shows(venue.id)),
      'upcoming_shows_count': len(find_upcoming_shows(venue.id))
    }
    venues_data.append(data)

  venue = list(filter(lambda d: d['id'] == venue_id, venues_data)) [0]
  return render_template('pages/show_venue.html', venue=venue)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueSubmit()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  try:
    print('I am in the create venue try block')
    venue = Venue(
      name = request.form['name'],
      city = request.form['city'],
      state = request.form['state'],
      address = request.form['address'],
      phone = request.form['phone'],
      genres = request.form['genres'],
      #website_link = request.form['website_link'], 
      #image_link = request.form['image_link'],
      facebook_link = request.form['facebook_link'],
      #seeking = request.form['seeking'],
      #seeking_description = request.form['seeking_description']
    )
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except():
    db.session.rollback()
    error = True
    flash('An error occured. Venue could not be listed!')
    print(sys.exc_info)
  finally:
    db.session.close()
  print('I am at the end of venue submit function')
  return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>/delete', methods=['GET', 'POST'])
def delete_venue(venue_id):
  venue = Venue.query.get(venue_id)
  error = False
  try:
    db.session.delete(venue)
    db.session.commit()
    flash('Venue was successfully deleted')
  except:
    db.session.rollback()
    flash('Error. Could not delete venue.')
    print('Error deleting venue')
    error = True
  finally:
    db.sessoin.close()
    return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  print('I am in artist area 1')
  artists = Artist.query.all()
  data = []
  for artist in artists:
    obj = {
      'id': artist.id,
      'name': artist.name
    }
    data.append(obj)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(
    Artist.name.ilike('%{}%'.format(search_term))).all()
  data = []

  for artist in artists:
    obj = {
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len(artist.shows)
    }
    data.append(obj)
    response = {
      "count": len(artists),
      "data": data
    }
  return render_template('pages/search_artist.html', results=response, search_term=search_term)
 

@app.route('/artists/<int:artist_id>')
def shows_artist(artist_id):
  print('I am in artist area 2')
  artists = Artist.query.all()
  shows = Shows.query.all()
  past_shows = []
  upcoming_shows = []

  
  print('I am in artist area 3')
  for shows in shows:
    current_date = datetime.now()
    shows_date = shows.date
    if shows_date > current_date:
      upcoming_shows.append(shows)
    else:
      past_shows.append(shows)
  

  def find_past_shows(artist_id):
    print('I am in artist area 4')
    if past_shows:
      for past_show in past_shows:
        if past_show.artist_id == artist_id:
          past_show_venue = Venue.query.get(past_show.venue_id)
          return [{
            'venue_id': past_show.venue_id,
            'venue_name': past_show_venue.name,
            'venue_image_link': past_show_venue.image_link,
            'start_time': str(past_show.date)
          }]
        else:
          return[]
    else:
      return []

  def find_upcoming_shows(artist_id):
    print('I am in artist area 5')
    if upcoming_shows:
      for upcoming_show in upcoming_shows:
        if upcoming_show.artist_id == artist_id:
          upcoming_show_venue = Venue.query.get(
            upcoming_show.venue_id)
          return [{
              'venue_id': upcoming_show.venue_id,
              'venue_name': upcoming_show_venue.name,
              'venue_image_link': upcoming_show_venue.image_link,
              'start_time': str(upcoming_show.date)
            }]
        else:
          return []
    else:
      return []

  artists_data = []
  for artist in artists:
    print('I am in artist area 6')
    data = {
     'id': artist.id,
     'name': artist.name,
     'genres': artist.genres,
     'city': artist.city,
     'state': artist.state,
     'phone': artist.phone,
     'website': artist.website_link,
     'facebook_link': artist.facebook_link,
     'seeking_venue': artist.seeking,
     'seeking_description': artist.seeking_description,
     'image_link': artist.image_link,
     'past_shows': find_past_shows(artist.id),
     'upcoming_shows': find_upcoming_shows(artist.id),
     'past_shows_count': len(find_past_shows(artist.id)),
     'upcoming_shows_count': len(find_upcoming_shows(artist.id))
    }
    artists_data.append(data)
  artist = list(filter(lambda d: d['id'] == artist_id, artists_data))[0]
  print('I am in artist area 7')
  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET', 'POST'])
def edit_artist(artist_id):
  error = False
  form = ArtistUpdate()
  artist = Artist.query.get(artist_id)
  
  if form.validate_on_submit():
    try: 
      artist.name = form.name.data 
      artst.city = form.city.data
      artist.state = form.city.data   
      artist.phone = form.phone.data   
      artist.genres = form.genres.data   
      artist_website_link = form.website_link.data   
      artist.facebook_link = form.facebook_link.data   
      artist.image_link = form.image_link.data   
      artist.seeking = form.seeking.data   
      artist.seeking_description = form.seeking_description.data   

      db.session. commit()
      flash('Successfully edited artist!')
    except:
      db.session.rolllback()
      flash('Error. Could not edit artist.')
      error = True
    finally:
      db.session.close()
      
    return redirect(url_for('index'))

  else: 
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.website_link.data = artist.website_link
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.seeking_description.data = artist.seeking_description

    return render_template('forms/edit_artist.html', form=form, artist=artist)




@app.route('/venues/<int:venue_id>/edit', methods=['GET', 'POST'])
def edit_venue(venue_id):
  form = VenueUpdate()
  venue = Venue.query.get(venue_id)
  error = False

  if form.validate_on_submit():
    try:
      venue.name = form.name.data   
      venue.city = form.city.data   
      venue.state = form.state.data   
      venue.address = form.address.data   
      venue.phone = form.phone.data   
      venue.genres = form.genres.data   
      venue.website_link = form.website_link.data   
      venue.facebook_link = form.facebook_link.data   
      venue.seeking = form.seeking.data   
      venue.seeking_description = form.seeking_description.data   
      db.session.commit()
      flash('Successfully edited venue!')
    except:
      db.session.rollback()
      flash('Error. Could not edit venue.')
      error = True
    finally:
      db.session.close()      
    return redirect(url_for('index'))
  elif request.method == 'GET':
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.website_link.data = venue.website_link
    form.image_link.data = venue.image_link
    form.seeking.data = venue.seeking
    form.seeking_description.data = venue.seeking_description
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistSubmit()
  return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  #if form.validate_on_submit():
  error = False
  print('I am in the IF statement create form')
  try:
    artist = Artist(
      name = request.form['name'],
      city = request.form['city'],
      state = request.form['state'],
      phone = request.form['phone'],
      genres = request.form.getlist('genres'),
      facebook_link = request.form['facebook_link']
    )
    print('I am trying to add new artist')
    db.session.add(artist)
    db.session.commit()
    flash('Artist was successfully listed!')
  except():
    print('I am in the error block')
    db.session.rollback()
    error = True
    flash('An error occured. Artist could not be listed')
    print(sys.exec_info)
  finally:
    db.session.close()
    print('I am in the close')
  print('I am at the end of create artist function')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Shows.query.all()
  data = []

  def find_venue_name(venueId):
    venue = Venue.query.get(venueId)
    return venue.name
  
  def find_artist_name(artistId):
    artist = Artist.query.get(artistId)
    return artist.name   
  
  def find_artist_image(artistId):
    artist = Artist.query.get(artistId)
    return artist.image_link
    
  for show in shows:
    obj={
      'venue_id': show.venue_id,
      'venue_name': find_venue_name(show.venue_id),
      'artist_id': show.artist_id,
      'artist_name': find_artist_name(show.artist_id),
      'artist_image_link': find_artist_image(show.artist_id),
      'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M") 
    }
    data.append(obj)

  return render_template('pages/shows.html', shows=data)


#  Create Show
#  ----------------------------------------------------------------

@app.route('/shows/create')
def create_shows():
  form = ShowSubmit()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_shows_submission():
  error = False
  try:
    show = Shows(
      artist_id = request.form['artist_id'],
      venue_id = request.form['venue_id'],
      start_time = show.start_time.strftime("%m/%d/%Y, %H:%M")
    )
    db.session.add(show)
    db.session.commit()
    flash('Successfully added a new show!')
    print('I am in show area 2s end ')
  except:
    db.session.rollback()
    flash('Error. Could not list new show')
    error = True
    print('I am in show area 3')
  finally:
    db.session.close()
    print('I am in show area 4')
  return render_template('pages/home.html')

#------------------------------------------------------------------------------------------------------
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
# Or specify port manually:
if __name__=='__main__':
    app.run(host='localhost', port=5000,debug=True)
