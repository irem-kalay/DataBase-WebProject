from flask import Flask, redirect, jsonify, url_for, request, render_template, Blueprint
from config import *
from utils.main_page_functions.tv_series_functions import *

# Create the Blueprint
tv_series_update_bp = Blueprint('tv_series_update', __name__)
tv_series_delete_bp = Blueprint('tv_series_delete', __name__)
tv_series_add_bp = Blueprint('tv_series_add', __name__)

episodes_add_bp = Blueprint('episodes_add', __name__)

episodes_delete_bp = Blueprint('episodes_delete', __name__)

# Episode silme route'u
@episodes_delete_bp.route('/delete_episode/<tconst>', methods=['POST'])
def delete_episode(tconst):
    try:
        cursor = mysql.connection.cursor()

        # title_episode tablosundan episode'u silme
        delete_query = """
        DELETE FROM title_episode WHERE tconst = %s
        """
        cursor.execute(delete_query, (tconst,))


        mysql.connection.commit()
        cursor.close()

        # Silme işleminden sonra, parent_tconst ile episodes sayfasına yönlendirme
        parent_tconst = fetch_parent_tconst(tconst)
        return redirect(url_for('tv_series_page'))

    except Exception as e:
        print(f"Error deleting episode: {e}")
        return render_template('error.html', message="Failed to delete episode."), 500


def fetch_parent_tconst(tconst):
    try:
        cursor = mysql.connection.cursor()
        query = """
            SELECT parentTconst
            FROM title_episode
            WHERE tconst = %s
        """
        cursor.execute(query, (tconst,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return result['parentTconst']
        else:
            print(f"No parentTconst found for tconst: {tconst}")
            return None
    except Exception as e:
        print(f"Error fetching parentTconst for tconst {tconst}: {e}")
        return None

def fetch_tconst_by_title(title):
    try:
        cursor = mysql.connection.cursor()
        query = """
            SELECT tconst
            FROM title_basics
            WHERE title = %s AND titleType = 'tv_series'
        """
        cursor.execute(query, (title,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return result['tconst']
        return None  # Return None if no matching tconst is found
    except Exception as e:
        print(f"Error fetching tconst for title {title}: {e}")
        return None



#Episodes ekleme route'u
@episodes_add_bp.route('/add_episode', methods=['GET', 'POST'])
def add_episode():
    # Eğer GET isteği ise, parentTconst parametresini URL'den alıyoruz.
    parent_tconst = None #default value

    if request.method == 'POST':
        # Kullanıcıdan alınan tconst
        tconst2 = request.form['tconst']#episode tconst girmek için

        tv_serie_title = request.form['tv_serie_title']
        tconst = fetch_tconst_by_title(tv_serie_title)

        parent_tconst= tconst #parent tconst burda
        title = request.form['title']
        seasonNumber = request.form['seasonNumber']
        episodeNumber = request.form['episodeNumber']
        genre = request.form['genre']  # Genre değerini formdan alıyoruz

        print(f"Fetched parent_tconst: {parent_tconst}")  # Debugging


        if not tconst or not parent_tconst or not genre:
            return render_template('error.html', message="Missing required fields: tconst, parentTconst or genre."), 400

        try:
            cursor = mysql.connection.cursor()

            # title_basics tablosuna ekleme
            query_basics = """
            INSERT INTO title_basics (tconst, title, titleType, isAdult, startYear, genre)
            VALUES (%s, %s, 'tv_episode', 0, YEAR(CURDATE()), %s)
            """
            cursor.execute(query_basics, (tconst2, title, genre))  # genre'yi buraya ekliyoruz

            # title_episode tablosuna ekleme
            query_episode = """
            INSERT INTO title_episode (tconst, parentTconst, seasonNumber, episodeNumber)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query_episode, (tconst2, parent_tconst, seasonNumber, episodeNumber))

            mysql.connection.commit()
            cursor.close()

            return redirect(url_for('episodes_details', tconst=parent_tconst))

        except Exception as e:
            print(f"Error adding episode: {e}")
            return render_template('error.html', message="Failed to add episode."), 500

    # parentTconst parametresi varsa, onu formda prepopulate ediyoruz
    return render_template('main_pages/CRUD_pages_main/tv_series_crud/add_episode.html', parent_tconst=parent_tconst)


#adding tv Series
@tv_series_add_bp.route('/add_tv_series', methods=['GET', 'POST'])
def add_tv_series():
    if request.method == 'POST':
        tconst = request.form['tconst']
        title = request.form['title']
        start_year = request.form['startYear']
        aka_title = request.form.get('akaTitle', None)
        rating = request.form.get('rating', None)

        end_Year = request.form.get('endYear')
        end_Year = int(end_Year)
        print(f"End Year: {end_Year}") #veri girilmiş endYear boş değil!!!

        # isAdult checkbox'ının değerini al
        is_adult = request.form['isAdult']

        if tconst is None:
            return render_template('error.html', message="Failed to generate tconst."), 500

        try:
            cursor = mysql.connection.cursor()
            query = """
            INSERT INTO title_basics (tconst, title, startYear, titleType, isAdult, endYear)
VALUES (%s, %s, %s, 'tv_series', %s, %s)
            """
            cursor.execute(query, (tconst, title, start_year, is_adult, end_Year))
            mysql.connection.commit()

            # 'title_akas
            if aka_title:
                query_aka = """
                INSERT INTO title_akas (tconst, title, country)
                SELECT tconst, %s, NULL FROM title_basics WHERE tconst = %s
                """
                cursor.execute(query_aka, (aka_title, tconst))
                mysql.connection.commit()

            # 'title_rating e rating ekliyor
            if rating:
                query_rating = """
                INSERT INTO title_rating (tconst, averageRating, numVotes)
                SELECT tconst, %s, 0 FROM title_basics WHERE tconst = %s
                """
                cursor.execute(query_rating, (rating, tconst))
                mysql.connection.commit()

            cursor.close()

            return redirect(url_for('tv_series_page'))


        except Exception as e:
            print(f"Error adding TV series: {e}")
            return render_template('error.html', message="Failed to add TV series."), 500

    return render_template('main_pages/CRUD_pages_main/tv_series_crud/add_tv_series.html')



#deleting tv series
@tv_series_delete_bp.route('/delete_tv_series/<string:tconst>', methods=['GET'])
def delete_tv_series_route(tconst):
    success = delete_tv_series(tconst)  # Deleting tv series based on tconst
    if success:
        return redirect(url_for('tv_series_page'))

    else:
        return render_template('error.html', message="Failed to delete TV series."), 500


#updating tv series
@tv_series_update_bp.route('/update_tv_series/<tconst>', methods=['GET', 'POST'])
def update_tv_series_route(tconst):
    try:
        cursor = mysql.connection.cursor()

        if request.method == 'POST':
            # Formdan gelen verileri al
            title = request.form['title']
            start_year = request.form['startYear']
            end_year = request.form.get('endYear', None)
            rating = request.form.get('rating', None)

            is_adult = request.form['isAdult']

            # Güncelleme sorgusu
            update_query = """
            UPDATE title_basics
            SET title = %s, startYear = %s, endYear = %s, isAdult = %s
            WHERE tconst = %s
            """
            cursor.execute(update_query, (title, start_year, end_year, is_adult, tconst))

            # Rating güncellemesi
            if rating:
                update_rating_query = """
                UPDATE title_rating
                SET averageRating = %s
                WHERE tconst = %s
                """
                cursor.execute(update_rating_query, (rating, tconst))

            mysql.connection.commit()
            cursor.close()

            return redirect(url_for('tv_series_page'))
        # Güncelleme sonrası TV serisi sayfasına dön

        # GET request: Mevcut verileri al ve formda göster
        query = """
        SELECT tb.title, tb.startYear, tb.endYear, tb.isAdult, 
               ta.title AS akaTitle, tr.averageRating
        FROM title_basics tb
        LEFT JOIN title_akas ta ON tb.tconst = ta.tconst
        LEFT JOIN title_rating tr ON tb.tconst = tr.tconst
        WHERE tb.tconst = %s
        """
        cursor.execute(query, (tconst,))
        series = cursor.fetchone()
        cursor.close()

        return render_template('main_pages/CRUD_pages_main/tv_series_crud/update_tv_series.html', series=series, tconst=tconst)

    except Exception as e:
        print(f"Error updating TV series: {e}")
        return render_template('error.html', message="Failed to update TV series."), 500


