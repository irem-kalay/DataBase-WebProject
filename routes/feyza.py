from flask import Flask, flash, redirect, request, Blueprint
from config import *
from utils.main_page_functions.directors_functions import *
from utils.detail_page_functions.names_functions import *
import requests
import base64

# Create the Blueprint
directors_delete_selected_bp = Blueprint('directors_delete_selected', __name__)
directors_update_bp = Blueprint('directors_update_selected', __name__)
directors_add_bp = Blueprint('directors_add', __name__)
names_add_bp = Blueprint('names_add', __name__)
names_update_bp = Blueprint('names_udpate', __name__)
names_delete_bp = Blueprint('names_delete', __name__)

# Delete selected directors (bulk deletion)
@directors_delete_selected_bp.route('/delete_selected_directors_route', methods=['POST'])
def delete_selected_directors_route():
    try:
        # Parse JSON data from the request
        data = request.get_json()
        selected_directors = data.get('selectedDirectors', [])
        
        if not selected_directors:
            return jsonify({'success': False, 'error': 'No directors selected for deletion.'})

        # Call the provided delete_selected_directors function
        delete_selected_directors(selected_directors)

        return jsonify({'success': True, 'message': 'Selected directors deleted successfully.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Delete a single director by NCONST
@directors_delete_selected_bp.route('/delete_director/<string:tconst>/<string:director_nconst>', methods=['DELETE'])
def delete_single_director(tconst, director_nconst):
    try:
        delete_director(tconst, director_nconst)
        return jsonify({'success': True, 'message': f'Director {director_nconst} deleted successfully.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
@directors_update_bp.route('/update_director/', methods=['POST'])
def update_director():
    # Parse the incoming JSON data
    data = request.get_json()
    print(data)

    # Extract individual fields from the JSON object
    productionTitle = data.get('productionTitle')
    directorName = data.get('directorName')
    writerName = data.get('writerName')
    yearDirected = data.get('yearDirected')
    rating = data.get('rating')
    tconst = data.get('tconst')
    writerNconst = data.get('writernconst')
    directorNconst = data.get('directornconst')
    print(productionTitle, directorName, writerName, yearDirected, rating, tconst, directorNconst,writerNconst)

    # print("ohaaa")
    return update_director_helper(productionTitle, directorName, writerName, yearDirected, rating, tconst, directorNconst, writerNconst)


@directors_add_bp.route('/fetch_movies_for_add', methods=['GET'])
def fetch_movies_for_add():
    try:
        cursor = mysql.connection.cursor()
        
        # Fetch the name details (original and known name)
        query_name = """
        SELECT tb.tconst, tb.title
        FROM title_basics tb
        LEFT JOIN title_crew tc ON tb.tconst = tc.tconst
        WHERE tc.directorNconst IS NULL;
        """
        
        # Execute the query first
        cursor.execute(query_name)
        
        # Fetch the results
        data = cursor.fetchall()  # Fetch the data after executing the query
        
        if not data:
            cursor.close()
            return None

        cursor.close()

        print(data)  # Check the fetched data in the console
        # ({'tconst': 1234567, 'title': 'Example Movie Title'},)
        # Process the data to match the required format
        tconsts = []
        for row in data:
            print(f"Row data: {row}")  # Debugging: Print each row
            if len(row) >= 2:  # Ensure that there are at least 2 columns (tconst, title)
                tconsts.append({"id": str(row['tconst']), "label": row['title']})
            else:
                print("Row does not contain the expected number of elements.")

        print({"tconsts": tconsts})

        return {"tconsts": tconsts}
    
    except Exception as e:
        print(f"Error: {e}")
        return None

# OUTOCOMPLETE YAPCAKTIM BI TURLU CALISMADI :(
@directors_add_bp.route('/fetch_names_for_add', methods=['GET'])
def fetch_names_for_add():
    try:
        cursor = mysql.connection.cursor()
        
        # Fetch the name details (original and known name)
        query_name = """
        SELECT nb.nconst, nb.originalName
        FROM name_basics nb
        LEFT JOIN title_crew tc ON nb.nconst = tc.directorNconst
        WHERE tc.directorNconst IS NOT NULL;
        """
        
        # Execute the query first
        cursor.execute(query_name)
        
        # Fetch the results
        data = cursor.fetchall()  # Fetch the data after executing the query
        
        if not data:
            cursor.close()
            return None

        cursor.close()

        print(data)  # Check the fetched data in the console
        # ({'tconst': 1234567, 'title': 'Example Movie Title'},)
        # Process the data to match the required format
        tconsts = []
        for row in data:
            print(f"Row data: {row}")  # Debugging: Print each row
            if len(row) >= 2:  # Ensure that there are at least 2 columns (tconst, title)
                tconsts.append({"id": str(row['nconst']), "label": row['originalName']})
            else:
                print("Row does not contain the expected number of elements.")

        print({"nconsts": tconsts})

        return {"nconsts": tconsts}
    
    except Exception as e:
        print(f"Error: {e}")
        return None


@directors_add_bp.route('/add_director_writer_relation/', methods=['POST'])
def add_director_writer_relation():
    # Parse the incoming JSON data
    data = request.get_json()

    # Extract individual fields from the JSON object
    tconst = data.get('tconst')
    nconst1 = data.get('nconst1')  # Director nconst
    nconst2 = data.get('nconst2')  # Writer nconst

    # Validate the required fields
    if not all([tconst, nconst1, nconst2]):
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    # Call the helper function to perform the database insertion
    return add_director_writer_relation_helper(tconst, nconst1, nconst2)

# Endpoint for adding name basics information
@names_add_bp.route('/add_name_basics/', methods=['POST'])
def add_name_basics():

    # Parse the incoming JSON data
    data = request.get_json()

    # Extract individual fields from the JSON object
    nconst = data.get('nconst')
    originalName = data.get('originalName')
    birthYear = data.get('birthYear')
    deathYear = data.get('deathYear')
    knownName = data.get('knownName')
    primaryProfession = data.get('primaryProfession')

    # Validate the required fields
    if not all([nconst, originalName, birthYear, knownName]):
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    # Call the helper function to perform the database insertion
    return add_name_basics_helper(nconst, originalName, birthYear, deathYear, knownName, primaryProfession)

@names_update_bp.route('/update_name_basics/', methods=['POST'])
def update_name():
    # Parse the incoming JSON data
    # print("buraya geldi")
    data = request.get_json()
    # print(f"buraya geldi {data}")
    # Extract individual fields from the JSON object
    name = data.get('name')
    knownName = data.get('knownName')
    birthYear = data.get('birthYear')
    deathYear = data.get('deathYear') if data.get('deathYear') else None  # If deathYear is empty, set it as None
    profession = data.get('profession') if data.get('profession') else None  # If primaryProfession is empty, set it as None
    nconst = data.get('nconst')
    # Log for debugging
    # print(f"Updating data for nconst {name}: {knownName}, {birthYear}, {deathYear}, {profession}, {nconst}")

    # Call the helper function to perform the database update
    return update_name_helper(name, knownName, birthYear, deathYear, profession, nconst)


@names_delete_bp.route('/delete_name_basics/', methods=['POST'])
def update_name():
    # Parse the incoming JSON data
    print("buraya geldi")
    data = request.get_json()
    print(f"buraya geldi {data}")
    # Extract individual fields from the JSON object
    nconst = data.get('nconst')
    # Log for debugging
    print(f"Updating data for nconst: {nconst}")

    # Call the helper function to perform the database update
    return delete_name_helper(nconst)
