# Bu sayfada route lar 'blueprint' denen sekilde kisaca eklenmeli
# Routes dosyasinda get ya da post yolunu tanimladiktan sonra (orda acikladim)
# bu sayfaya gelip app.register_blueprint() fonksiyonuyla eklemeniz gerekiyor.

from flask import render_template, request
from config import *
# Import functions from detail_page_functions
from utils.detail_page_functions.crew_and_cast_functions import *
from utils.detail_page_functions.episodes_functions import *
from utils.detail_page_functions.names_functions import *
from utils.detail_page_functions.title_functions import *
# Import functions from main_page_functions
from utils.main_page_functions.actors_functions import *
from utils.main_page_functions.directors_functions import *
from utils.main_page_functions.movies_functions import *
from utils.main_page_functions.tv_series_functions import *
# Import other routes from routes
from routes.feyza import *
from routes.irem import *
from routes.meric import *
from routes.rahim import *

app = Flask(__name__)
mysql = MySQL(app)
app.config.from_object(Config)

######### BLUEPRINT REGISTERING #########
app.register_blueprint(directors_delete_selected_bp)
app.register_blueprint(directors_update_bp)
app.register_blueprint(directors_add_bp)
app.register_blueprint(names_add_bp)
app.register_blueprint(names_update_bp)
app.register_blueprint(names_delete_bp)

app.register_blueprint(tv_series_update_bp, url_prefix='/update_tv_series')
app.register_blueprint(tv_series_delete_bp, url_prefix='/delete_tv_series')
app.register_blueprint(tv_series_add_bp, url_prefix='/add_tv_series')

app.register_blueprint(rating_aka_update_page_bp)
app.register_blueprint(movies_update_page_bp)

app.register_blueprint(episodes_add_bp, url_prefix='/add_episode')
app.register_blueprint(episodes_delete_bp, url_prefix='/delete_episode')




######### MAIN PAGE ROUTE #########
@app.route('/')
def main_page():
    return render_template('main_page.html')


######### SORTABLE MAIN PAGE ROUTES #########

@app.route('/tv_series', methods=['GET'])
def tv_series_page():
    search_query = request.args.get('search_query', '')
    order = request.args.get('order', default='ASC', type=str)  # Sıralama yönü (ASC/DESC)

    # `order` parametresine göre tv_series verilerini al
    tv_series = get_tv_series(search_query, order)

    year = request.args.get('year', default=2024, type=int)  # Yıl filtresi
    print(f"Received year: {year}")  # Log: year kontrolü

    best_year_series = get_best_year_series(year)

    if tv_series is None:
        return render_template('error.html', message="Failed to load TV series data."), 500

    return render_template('/main_pages/tv_series.html', tv_series=tv_series, best_year_series=best_year_series,
                           selected_year=year, order=order)

@app.route('/movies', methods=['GET'])
def movies_page():

    sort_by = request.args.get('sort_by')  
    sort_order = request.args.get('sort_order')  
    filter_by = request.args.get('filter_by')  
    filter_value = request.args.get('filter_value')  

    # Fetch movies with the provided sorting and filtering options
    movies = get_movies(sort_by=sort_by, sort_order=sort_order, filter_by=filter_by, filter_value=filter_value)

    if movies is None:
        return render_template('error.html', message="Failed to load movies data."), 500

    return render_template('/main_pages/movies.html', movies=movies)


@app.route('/directors', methods=['GET'])
def directors_page():
    # Retrieve query parameters for filtering and sorting
    sort_by = request.args.get('sort_by')
    filter_by = request.args.get('filter_by')
    filter_value = request.args.get('filter_value')
    rating = request.args.get('rating')
    rating_condition = request.args.get('rating_condition')
    year = request.args.get('year')
    year_condition = request.args.get('year_condition')

    # Pass parameters to the get_directors function
    directors = get_directors(
        sort_by=sort_by,
        filter_by=filter_by,
        filter_value=filter_value,
        rating=rating,
        rating_condition=rating_condition,
        year=year,
        year_condition=year_condition
    )

    # Handle case where data retrieval fails
    if directors is None:
        return render_template('error.html', message="Failed to load TV series data."), 500

    # Render the template with the retrieved data
    return render_template('/main_pages/directors.html', directors=directors)


@app.route('/actors')
def actors_page():
    actors = get_actors()
    if actors is None:
        return render_template('error.html', message="Failed to load TV series data."), 500
    return render_template('/main_pages/actors.html', actors=actors)


######### DETAIL PAGE ROUTES #########
@app.route('/episodes/<tconst>')
def episodes_details(tconst):
    episodes = fetch_episodes_by_tconst(tconst)
    return render_template('/detail_pages/episodes.html', episodes=episodes)


@app.route('/title/<string:tconst>')
def title_details(tconst):
    movie = fetch_title_by_tconst(tconst)
    print(movie)
    return render_template('detail_pages/title.html', movie=movie)

@app.route('/names/<int:nconst>')
def names_details(nconst):
    images = [f"indir ({i}).jpeg" for i in range(5)]  
    selected_image = random.choice(images)  
    data = fetch_names_by_nconst(nconst)
    return render_template('detail_pages/names.html', data=data, image_path=selected_image)

@app.route('/crew_and_cast/<nconst>')
def crew_and_cast_details(nconst):
    crew_and_cast = fetch_crew_and_cast_by_nconst(nconst)
    return render_template('/detail_pages/crew_and_cast.html', crew_and_cast=crew_and_cast)


######### RUN THE WEBPAGE #########
if __name__ == '__main__':
    app.run(debug=True)


