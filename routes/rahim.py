from flask import Flask, redirect, jsonify, url_for, request, render_template, Blueprint
from config import *
from utils.main_page_functions.movies_functions import *
from utils.detail_page_functions.title_functions import *

# Create the Blueprint
rating_aka_update_page_bp = Blueprint('rating_aka_update_page', __name__)
movies_update_page_bp = Blueprint('movies_update_page', __name__)

# app.route demek yerine blueprint_name.bp olcak artik

# blueprint kullanimi:
# @blueprint_name.route('/route_name', methods=['POST or GET'])
# def fonksiyon():

# GET Route to display movie details for updating

#---------------------------------------------rating aka-----------------------------------------------------------------
@rating_aka_update_page_bp.route('/rating_aka_update/<string:tconst>', methods=['GET'])
def rating_aka_update_get(tconst):
    try:
        result = fetch_information_update_page(tconst)
        print(result)
        if result.get('rating') is None and  result.get('akas') == []:
            # Hem rating hem de aka verisi eksikse
            return render_template('main_pages/CRUD_pages_main/rating_aka_crud/rating_aka_missing.html', result=result)

        elif result.get('rating') is None and result.get('akas') != []:
            # Yalnızca rating eksikse
            return render_template('main_pages/CRUD_pages_main/rating_aka_crud/rating_missing.html', result=result)

        elif result.get('akas') == [] and result.get('rating') is not  None:
            # Yalnızca aka verisi eksikse
            return render_template('main_pages/CRUD_pages_main/rating_aka_crud/aka_missing.html', result=result)
        else:
            # Rating ve aka verileri varsa
            return render_template('main_pages/CRUD_pages_main/rating_aka_crud/rating_aka_update.html', result=result)

    except Exception as e:
        print(f"Error fetching movie {tconst}: {e}")
        return f"An error occurred: {e}", 500
    


@rating_aka_update_page_bp.route('/rating_update/<string:tconst>', methods=['POST'])
def rating_update_post(tconst):
    try:
        cursor = mysql.connection.cursor()

        # Get form data
        form_data = request.form  
        print(form_data)

        new_rating = form_data.get('rating')
        new_votes = form_data.get('votes')


        if new_rating and new_votes:
            # Convert the form data to appropriate types
            new_rating = float(new_rating)
            new_votes = int(new_votes)

            # Update the rating and votes for the given tconst
            query = """
                UPDATE title_rating 
                SET averageRating = %s, numVotes = %s
                WHERE tconst = %s
            """


            cursor.execute(query, (new_rating, new_votes, tconst))

            mysql.connection.commit()

            result = fetch_information_update_page(tconst)
            return render_template('main_pages/CRUD_pages_main/rating_aka_crud/rating_aka_update.html', result=result)

        else:
            return "Invalid data: Rating and votes must be provided.", 400

    except Exception as e:
        print(f"Error updating movie {tconst}: {e}")
        return f"An error occurred: {e}", 500


@rating_aka_update_page_bp.route('/aka_update/<string:tconst>', methods=['POST'])
def aka_update_post(tconst):
    try:
        cursor = mysql.connection.cursor()

        # Get the form data
        form_data = request.form

        # Update akas
        for key in form_data:
            if key.startswith('akas['):
                index = int(key.split('[')[1].split(']')[0])
                title = form_data.get(f'akas[{index}][title]')
                country = form_data.get(f'akas[{index}][country]')
                is_original = form_data.get(f'akas[{index}][isOriginal]') == 'on'

                ordering = index  # Assuming ordering corresponds directly to form index

                
                aka_query = """
                    UPDATE title_akas
                    SET title = %s, country = %s, isOriginal = %s
                    WHERE tconst = %s AND ordering = %s
                """
                print(aka_query)
                cursor.execute(aka_query, (title, country, is_original, tconst, ordering))

        # Commit the transaction
        mysql.connection.commit()

        # Fetch the updated information and render the page
        result = fetch_information_update_page(tconst)
        return render_template('main_pages/CRUD_pages_main/rating_aka_crud/rating_aka_update.html', result=result)

    except Exception as e:
        print(f"Error occurred: {e}")
        mysql.connection.rollback()
        return "An error occurred while updating the data.", 500

    finally:
        cursor.close()


@rating_aka_update_page_bp.route('/delete_rating/<string:tconst>', methods=['POST'])
def delete_rating_post(tconst):
    try:
        cursor = mysql.connection.cursor()
        
        # Silme sorgusu
        delete_query = """
            DELETE FROM title_rating
            WHERE tconst = %s
        """
        cursor.execute(delete_query, (tconst,))
        mysql.connection.commit()

        return rating_aka_update_get(tconst)

    except Exception as e:
        print(f"Error deleting rating for movie {tconst}: {e}")
        return f"An error occurred: {e}", 500

@rating_aka_update_page_bp.route('/delete_aka/<string:tconst>/<string:ordering>', methods=['POST'])
def delete_aka_post(tconst, ordering):
    try:
        cursor = mysql.connection.cursor()
        
        delete_query = """
            DELETE FROM title_akas
            WHERE tconst = %s AND ordering = %s
        """
        cursor.execute(delete_query, (tconst, ordering))
        mysql.connection.commit()

        result = fetch_information_update_page(tconst)
        return render_template('main_pages/CRUD_pages_main/rating_aka_crud/rating_aka_update.html', result=result)

    except Exception as e:
        print(f"Error deleting aka for movie {tconst}: {e}")
        return f"An error occurred: {e}", 500

@rating_aka_update_page_bp.route('/rating_add/<string:tconst>', methods=['POST'])
def rating_add(tconst):
    try:
        # Get the form data
        rating = request.form.get('rating')
        votes = request.form.get('votes')

        cursor = mysql.connection.cursor()

        query = """
            INSERT INTO title_rating (tconst, averageRating, numVotes)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (tconst, rating, votes))
        mysql.connection.commit()

        cursor.close()

        # Redirect to the movie details page
        return rating_aka_update_get(tconst)

    except Exception as e:
        return rating_aka_update_get(tconst)
    

@rating_aka_update_page_bp.route('/aka_add/<string:tconst>', methods=['POST'])
def aka_add(tconst):
    try:
        new_aka_title = request.form.get('new_aka_title')
        new_aka_country = request.form.get('new_aka_country')
        new_aka_isOriginal = 'new_aka_isOriginal' in request.form

        # Check if both title and country are provided
        if not new_aka_title or not new_aka_country:

            return redirect(url_for('rating_aka_update_page', tconst=tconst))

        cursor = mysql.connection.cursor()

        # Query to get the highest ordering for the given tconst
        cursor.execute("""
            SELECT MAX(ordering) AS max_ordering
            FROM title_akas
            WHERE tconst = %s
        """, (tconst,))
        result = cursor.fetchone()

        # Calculate the new ordering (next available ordering)
        new_ordering = result['max_ordering'] + 1 if result['max_ordering'] is not None else 1

        # Insert the new Aka with the calculated ordering
        query = """
            INSERT INTO title_akas (tconst, ordering, title, country, isOriginal)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (tconst, new_ordering, new_aka_title, new_aka_country, new_aka_isOriginal))
        mysql.connection.commit()
        cursor.close()

        return rating_aka_update_get(tconst)

    except Exception as e:
        print(f"Error adding new Aka for {tconst}: {e}")
        return rating_aka_update_get(tconst)




#---------------------------------------------rating aka-----------------------------------------------------------------

#------------------------------------------------movies-------------------------------------------------------------------

@movies_update_page_bp.route('/movies_update/<string:tconst>', methods=['GET'])
def movies_update_post(tconst):
    try:
        result = fetch_title_by_tconst(tconst)
        return render_template('main_pages/CRUD_pages_main/movies_crud/movies_update.html', result=result)

    except Exception as e:
        print(f"Error fetching movie {tconst}: {e}")
        return f"An error occurred: {e}", 500

@movies_update_page_bp.route('/title_update/<string:tconst>', methods=['POST'])
def update_movie_details(tconst):
    try:
        # Fetch form data
        genre = request.form.get('genre')
        title_type = request.form.get('title_type')
        title = request.form.get('title')
        is_adult = request.form.get('is_adult') == 'on'  # Checkbox value
        start_year = request.form.get('start_year')
        end_year = request.form.get('end_year')

        # Validate required fields
        if not genre or not title_type or not title or not start_year:
            return "Missing required fields", 400

        # Database update logic
        cursor = mysql.connection.cursor()
        update_query = """
            UPDATE title_basics 
            SET 
                genre = %s, 
                titleType = %s, 
                title = %s, 
                isAdult = %s, 
                startYear = %s, 
                endYear = %s
            WHERE tconst = %s
        """
        cursor.execute(update_query, (
            genre, title_type, title, is_adult, start_year, end_year if end_year else None, tconst
        ))
        mysql.connection.commit()
        cursor.close()

        # Redirect or send success response
        return redirect(f'/movies_update/{tconst}')  # Redirect back to view the updated record

    except Exception as e:
        print(f"Error updating movie {tconst}: {e}")
        return f"An error occurred: {e}", 500

@movies_update_page_bp.route('/movies_delete/<string:tconst>', methods=['POST'])
def delete_movie(tconst):
    try:

        cursor = mysql.connection.cursor()
        delete_query = "DELETE FROM title_basics WHERE tconst = %s"
        cursor.execute(delete_query, (tconst,))
        mysql.connection.commit()
        cursor.close()

        return redirect('/movies') 

    except Exception as e:
        print(f"Error deleting movie {tconst}: {e}")
        return f"An error occurred: {e}", 500
    
@movies_update_page_bp.route('/add_title_basics_page', methods=['GET'])
def add_title_basics_page():
    return render_template("/main_pages/CRUD_pages_main/movies_crud/movies_add.html")

@movies_update_page_bp.route('/add_title_basics', methods=['POST'])
def title_add():
    tconst = request.form['tconst']  # Get tconst from the form
    genre = request.form['genre']
    title_type = request.form['title_type']
    title = request.form['title']
    is_adult = 'is_adult' in request.form  # Checkbox may or may not be checked
    start_year = request.form['start_year']
    end_year = request.form['end_year']
    cursor = mysql.connection.cursor()
    print("buraya geldi")
    
    query = """
                INSERT INTO title_basics 
                    (genre, titleType, title, isAdult, startYear, endYear, tconst)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
    
    cursor.execute(query, (genre, title_type, title, is_adult, start_year, end_year, tconst))
    mysql.connection.commit()
    cursor.close()
    
    return redirect('/movies') 





#------------------------------------------------movies-------------------------------------------------------------------

def fetch_information_update_page(tconst): 
    try:
        cursor = mysql.connection.cursor()

        # Query for title_rating (rating and votes)
        query_rating = """
            SELECT 
                tr.averageRating AS rating,
                tr.numVotes AS votes
            FROM 
                title_rating tr
            WHERE 
                tr.tconst = %s
        """
        cursor.execute(query_rating, (tconst,))
        rating_result = cursor.fetchall()


        rating = rating_result[0]['rating'] if rating_result else None
        votes = rating_result[0]['votes'] if rating_result else None

        # Query for title_akas (title, country, isOriginal)
        query_akas = """
            SELECT 
                ta.title,
                ta.country,
                ta.isOriginal
            FROM 
                title_akas ta
            WHERE 
                ta.tconst = %s
        """
        cursor.execute(query_akas, (tconst,))
        akas_result = cursor.fetchall()


        akas = [{'title': row['title'], 'country': row['country'], 'isOriginal': row['isOriginal']} for row in akas_result] if akas_result else []

        if akas and akas[0]['title'] is None: 
            akas = []

        return {'id': tconst, 'rating': rating, 'votes': votes, 'akas': akas}

    except Exception as e:
        print(f"Error fetching movie {tconst}: {e}")
        return f"An error occurred: {e}", 500
