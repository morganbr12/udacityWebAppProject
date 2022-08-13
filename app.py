# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

# import json
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

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# TODO: connect to a local postgresql database

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    seeking_link = db.Column(db.String(), nullable=False)
    seeking_description = db.Column(db.String(), nullable=False)
    shows = db.relationship('Show', backref='shown', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    def __repr__(self):
        return f'<Venue {self.id}, name: {self.name}, city: {self.city} state: {self.state}, ' \
               f'address: {self.address}, ' \
               f'phone: {self.phone}, image_link: {self.image_link}, facebook_link: {self.facebook_link},' \
               f'seeking_link: {self.seeking_link}, seeking_description: {self.seeking_description}>'


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    seeking_link = db.Column(db.String(), nullable=False)
    seeking_description = db.Column(db.String(), nullable=False)
    shows = db.relationship('Show', backref='show', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    def __repr__(self):
        return f'<Artist_id: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, ' \
               f'phone: {self.phone}, genres: {self.genres}, image_link: {self.image_link}, ' \
               f'facebook_link: {self.facebook_link}, seeking_link: {self.seeking_link}, ' \
               f'seeking_description: {self.seeking_description}>'


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = "show"
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime(), nullable=False)
    artists_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    time_current = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    show_venues = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()
    ven_st_and_cty = ''
    data = []

    for ven in show_venues:
        # new_coming_shows = ven.shows.filter(Show.start_city > time_current)
        if ven_st_and_cty == ven.city + ven.state:
            data[len(data) - 1]["show_venues"].append({
                'id': ven.id,
                'name': ven.name,
                # 'upcoming_show': len(new_coming_shows)
            })

        else:
            ven_st_and_cty == ven.city + ven.state
            data.append({
                "city": ven.city,
                "state": ven.state,
                "venues": [{
                    "id": ven.id,
                    "name": ven.name,
                    # "upcoming_show": len(new_coming_shows)
                }]
            })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    venue_search = Venue.query.filter(Venue.name.ilike('%' + request.form['search_term'] + '%'))
    list_venue = list(map(venue_search, Venue.short))
    response = {
        "count": len(list_venue),
        "data": list_venue
    }

    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue_search = Venue.qet(venue_id)
    if venue_search:
        venue_details = Venue.detail(venue_search)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:S")
        new_shows_query = Show.query.options(db.joinedload(Show.Venue)) \
            .filter(Show.venue_id == venue_id).filter(Show.start_item > current_time).all()
        new_show = list(map(Show.artist_details, new_shows_query))
        venue_details["new_coming_shows"] = new_show
        venue_details["upcoming_shows_count"] = len(new_show)
        past_shows_query = Show.query.options(db.joinedloading(Show.venue))\
            .filter(Show.venue_id == venue_id).filter(
            Show.start_item <= current_time).all()
        past_shows = list(map(Show.artist_details, past_shows_query))
        venue_details["past_shows"] = past_shows
        venue_details["past_shows_count"] = len(past_shows)
        data = Venue.query.filter_by(venue_id=venue_id).order_by('id').all()

        return render_template('pages/show_venue.html', venue=venue_datails)
    return render_template('errors/404.html')


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
    form = VenueForm(request.form)
    error = False
    body = {}
    try:
        new_venue = Venue(
            name=request.form['name'],
            genres=request.form.getlist('genres'),
            address=request.form['address'],
            city=request.form['city'],
            state=request.form['state'],
            phone=request.form['phone'],
            website=request.form['website'],
            facebook_link=request.form['facebook_link'],
            image_link=request.form['image_link'],
            seeking_talent=request.form['seeking_talent'],
            description=request.form['seeking_description'],
        )
        # venue = Venue(new_venue)
        db.session.add(new_venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        # body['new_venue']
    except SQLAlchemyError as e:
        error = True
        flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        db.session.rollback()
    finally:
        db.session.close()
    # on successful db insert, flash success

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')

    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    artists_data_query = Artist.query.filter(Artist.name.ilike('%' + request.form['search_term'] + '%'))
    artists_list = list(map(Artist.short, artists_data_query))
    response = {
        "count": len(artists_list),
        "data": artists_list
    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    data_query = Artist.query.get(artist_id)
    if data_query:
        artists_details = Artist.details(data_query)
        time_current = datetime.now().strftime('%Y-%m-%d %H:%M')
        show_query = Show.query.options(db.joinedload(Show.Artist)) \
            .filter(Show.artist_id == artist_id).filter(Show.start_time > time_current).all()
        show_list = list(map(Show.venue_details, show_query))
        artists_details["new_coming_shows"] = show_list
        artists_details["upcoming_show_count"] = len(show_list)
        p_show_query_data = Show.query.options(db.joinedload(Show.Artist)) \
            .filter(Show.artist_id == artist_id).filter(Show.start_time <= time_current).all()
        p_show_data_list = list(map(Show.venue_details, p_show_query_data))
        artists_details["past_shows"] = p_show_data_list
        artists_details["p_show_count"] = len(p_show_data_list)

        # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
        return render_template('pages/show_artist.html', artist=data_query)
    return render_template('errors/404.html')


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm(request.form)
    artist_data_info = Artist.query.get(artist_id)

    if artist_data_info:
        artist_details = Artist.details(artist_data)
        form.name.data = artist_details["name"]
        form.genres.data = artist_details["genres"]
        form.city.data = artist_details["city"]
        form.state.data = artist_details["state"]
        form.phone.data = artist_details["phone"]
        form.website.data = artist_details["website"]
        form.facebook_link.data = artist_details["facebook_link"]
        form.seeking_venue.data = artist_details["seeking_venue"]
        form.seeking_description.data = artist_details["seeking_description"]
        form.image_link.data = artist_details["image_link"]

        return render_template('forms/edit_artist.html', form=form, artist=artist_details_info)
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('errors/404.html')


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    from_form = ArtistForm(request.form)
    artist_data_request = Artist.query.get(artist_id)

    if artist_data_request:
        if form.validate():
            seeking_venue = False
            seeking_description = ''
            if 'seeking_venue' in request.form:
                seeking_venue = request.form['seeking_venue'] == 'y'
            if 'seeking_description' in request.form:
                seeking_description = request.form['seeking_description']
            setattr(artist_data_request, 'name', request.form['name'])
            setattr(artist_data_request, 'genres', request.form.getlist('genres'))
            setattr(artist_data_request, 'city', request.form['city'])
            setattr(artist_data_request, 'state', request.form['state'])
            setattr(artist_data_request, 'phone', request.form['phone'])
            setattr(artist_data_request, 'website', request.form['website'])
            setattr(artist_data_request, 'facebook_link', request.form['facebook_link'])
            setattr(artist_data_request, 'image_link', request.form['image_link'])
            setattr(artist_data_request, 'seeking_description', seeking_description)
            setattr(artist_data_request, 'seeking_venue', seeking_venue)

            Artist.update(artist_data_request)
            return redirect(url_for('show_artist', artist_id=artist_id))
        else:
            print(form.errors)
    return render_template('errors/404.html')


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue_data = Venue.query.get(venue_id)

    if venue_data:
        venue = Venue.detail(venue_query)
        form.name.data = venue["name"]
        form.genres.data = venue["genres"]
        form.address.data = venue["address"]
        form.city.data = venue["city"]
        form.state.data = venue["state"]
        form.phone.data = venue["phone"]
        form.website.data = venue["website"]
        form.facebook_link.data = venue["facebook_link"]
        form.seeking_talent.data = venue["seeking_talent"]
        form.seeking_description.data = venue["seeking_description"]
        form.image_link.data = venue["image_link"]

        # TODO: populate form with values from venue with ID <venue_id>
        return render_template('forms/edit_venue.html', form=form, venue=venue)
    return render_template('errors/500.html')


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    form = VenueForm(request.form)
    venue_data = Venue.query.get(venue_id)
    if venue_data:
        if form.validate():
            seeking_talent = False
            seeking_description = ''
            if 'seeking_talent' in request.form:
                seeking_talent = request.form['seeking_talent'] == 'y'
            if 'seeking_description' in request.form:
                seeking_description = request.form['seeking_description']
            setattr(venue_data, 'name', request.form['name'])
            setattr(venue_data, 'genres', request.form.getlist('genres'))
            setattr(venue_data, 'address', request.form['address'])
            setattr(venue_data, 'city', request.form['city'])
            setattr(venue_data, 'state', request.form['state'])
            setattr(venue_data, 'phone', request.form['phone'])
            setattr(venue_data, 'website', request.form['website'])
            setattr(venue_data, 'facebook_link', request.form['facebook_link'])
            setattr(venue_data, 'image_link', request.form['image_link'])
            setattr(venue_data, 'seeking_description', seeking_description)
            setattr(venue_data, 'seeking_talent', seeking_talent)
            Venue.update(venue_data)
            return redirect(url_for('show_venue', venue_id=venue_id))
        else:
            print(form.errors)
    return render_template('errors/500.html')


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

    try:
        seeking_venue = False
        seeking_description = ''
        if 'seeking_venue' in request.form:
            seeking_venue = request.form['seeking_venue'] == 'y'
        if 'seeking_description' in request.form:
            seeking_description = request.form['seeking_description']
        new_artist = Artist(
            name=request.form['name'],
            genres=request.form['genres'],
            city=request.form['city'],
            state=request.form['state'],
            phone=request.form['phone'],
            website=request.form['website'],
            image_link=request.form['image_link'],
            facebook_link=request.form['facebook_link'],
            seeking_venue=seeking_venue,
            seeking_description=seeking_description,
        )
        Artist.insert(new_artist)
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    except SQLAlchemyError as e:
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    query_show = Show.query.options(db.joinedload(Show.Venue)).all()
    data = list(map(Show.details, query_show))

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
    try:
        new_show = Show(
            venue_id=request.form['venue_id'],
            artist_id=request.form['artist_id'],
            start_time=request.form['start_time'],
        )
        Show.insert(new_show)
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    except SQLAlchemyError as e:
        flash('An error occurred. Show could not be listed.')
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
