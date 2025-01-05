from flask import Flask, jsonify, render_template
from flask_mysqldb import MySQL
from config import Config  # Import the Config class from config.py

app = Flask(__name__, template_folder="../../templates")

# Load app configuration from config.py
app.config.from_object(Config)

# Initialize MySQL connection
mysql = MySQL(app)

def fetch_title_by_tconst(tconst):
    
        cursor = mysql.connection.cursor()
        query = """

        SELECT
            tb.titleType
        FROM
            title_basics tb
        WHERE tb.tconst = %s

        """
        cursor.execute(query, (tconst,)) 
        data = cursor.fetchall()
        cursor.close()

        if data[0]['titleType'] == "tv_episode":
            
            try:


                query = """
                SELECT 
                    tb.tconst,
                    tb.titleType,
                    tb.title,
                    tb.isAdult,
                    tb.startYear,
                    tb.endYear,
                    tb.genre,
                    tc.directorNconst,
                    director.originalName AS directorName,
                    tc.writerNconst,
                    writer.originalName AS writerName,
                    tr.averageRating,
                    tr.numVotes,
                    te.parentTconst,
                    ta.title AS akaTitle,
                    ta.country AS akaCountry,
                    ta.isOriginal AS akaIsOriginal,
                    tcst.nconst AS castNconst,
                    cast.originalName AS castName,
                    tcst.category AS castCategory,
                    tcst.characterName AS castCharacter
                FROM 
                    title_basics tb
                LEFT JOIN title_crew tc 
                    ON tb.tconst = tc.tconst
                LEFT JOIN name_basics director 
                    ON tc.directorNconst = director.nconst
                LEFT JOIN name_basics writer 
                    ON tc.writerNconst = writer.nconst
                LEFT JOIN title_rating tr 
                    ON tb.tconst = tr.tconst
                LEFT JOIN title_episode te 
                    ON tb.tconst = te.tconst
                LEFT JOIN title_akas ta 
                    ON tb.tconst = ta.tconst
                LEFT JOIN title_cast tcst 
                    ON tb.tconst = tcst.tconst
                LEFT JOIN name_basics cast 
                    ON tcst.nconst = cast.nconst
                WHERE tb.tconst = %s
                """
                
                cursor = mysql.connection.cursor()
                cursor.execute(query, (tconst,)) 
                data = cursor.fetchall()
                cursor.close()

                if not data:
                    return None 
                
                title_info = {
                    "tconst": data[0]['tconst'],
                    "title": data[0]['title'],
                    "title_type": data[0]['titleType'],
                    "is_adult": data[0]['isAdult'],
                    "start_year": data[0]['startYear'],
                    "end_year": data[0]['endYear'],
                    "genre": data[0]['genre'],
                    "director_name": data[0]['directorName'],
                    "writer_name": data[0]['writerName'],
                    "average_rating": data[0]['averageRating'],
                    "num_votes": data[0]['numVotes'],
                    "parent_tconst": data[0]['parentTconst']
                }

                cast_info = {}
                aka_info = {}

                for row in data:

                    cast_info[(row['castNconst'], row['castCategory'], row['castCharacter'])] = {
                        'nconst': row['castNconst'],
                        'original_name': row['castName'],
                        'category': row['castCategory'],
                        'character_name': row['castCharacter'],  # Remove any trailing whitespace
                    }

                    # Aka info, using a dictionary to remove duplicates
                    aka_info[(row['akaTitle'], row['akaCountry'], row['akaIsOriginal'])] = {
                        'aka_title': row['akaTitle'],
                        'aka_country': row['akaCountry'],
                        'aka_is_original': row['akaIsOriginal'],
                    }

                # Convert the dictionaries back to lists
                title_info["cast"] = list(cast_info.values())
                title_info["aka"] = list(aka_info.values())
                return title_info

            except Exception as e:
                print(f"Error fetching title for tconst {tconst}: {e}")
                return None

        elif data[0]['titleType'] == "tv_series":
            try:

                query = """
                SELECT 
                    tb.tconst,
                    tb.titleType,
                    tb.title,
                    tb.isAdult,
                    tb.startYear,
                    tb.endYear,
                    tb.genre,
                    tc.directorNconst,
                    director.originalName AS directorName,
                    tc.writerNconst,
                    writer.originalName AS writerName,
                    tr.averageRating,
                    tr.numVotes,
                    te.seasonNumber,
                    te.episodeNumber,
                    ta.title AS akaTitle,
                    ta.country AS akaCountry,
                    ta.isOriginal AS akaIsOriginal,
                    tcst.nconst AS castNconst,
                    cast.originalName AS castName,
                    tcst.category AS castCategory,
                    tcst.characterName AS castCharacter
                FROM 
                    title_basics tb
                LEFT JOIN title_crew tc 
                    ON tb.tconst = tc.tconst
                LEFT JOIN name_basics director 
                    ON tc.directorNconst = director.nconst
                LEFT JOIN name_basics writer 
                    ON tc.writerNconst = writer.nconst
                LEFT JOIN title_rating tr 
                    ON tb.tconst = tr.tconst
                LEFT JOIN title_episode te 
                    ON tb.tconst = te.parentTconst
                LEFT JOIN title_akas ta 
                    ON tb.tconst = ta.tconst
                LEFT JOIN title_cast tcst 
                    ON tb.tconst = tcst.tconst
                LEFT JOIN name_basics cast 
                    ON tcst.nconst = cast.nconst
                WHERE tb.tconst = %s
                """
                
                cursor = mysql.connection.cursor()
                cursor.execute(query, (tconst,)) 
                data = cursor.fetchall()
                cursor.close()

                if not data:
                    return None  # No data found for the given tconst
                title_info = {
                    "tconst": data[0]['tconst'],
                    "title": data[0]['title'],
                    "title_type": data[0]['titleType'],
                    "is_adult": data[0]['isAdult'],
                    "start_year": data[0]['startYear'],
                    "end_year": data[0]['endYear'],
                    "genre": data[0]['genre'],
                    "director_name": data[0]['directorName'],
                    "writer_name": data[0]['writerName'],
                    "average_rating": data[0]['averageRating'],
                    "num_votes": data[0]['numVotes'],
                }

              
                cast_info = {}
                aka_info = {}
                episodes_set = set() 
                episodes = []

                for row in data:
                    
                    
                    cast_info[(row['castNconst'], row['castCategory'], row['castCharacter'])] = {
                        'nconst': row['castNconst'],
                        'original_name': row['castName'],
                        'category': row['castCategory'],
                        'character_name': row['castCharacter'],  
                    }

                    
                    aka_info[(row['akaTitle'], row['akaCountry'], row['akaIsOriginal'])] = {
                        'aka_title': row['akaTitle'],
                        'aka_country': row['akaCountry'],
                        'aka_is_original': row['akaIsOriginal'],
                    }

                    # If the title is a TV series, add the episode information
                    episode = (row['seasonNumber'], row['episodeNumber'], row['title'])
                    if episode not in episodes_set:
                        episodes.append({
                            'season_number': row['seasonNumber'],
                            'episode_number': row['episodeNumber'],
                            'episode_title': row['title'],
                        })
                        episodes_set.add(episode)

                # Convert the dictionaries back to lists
                title_info["cast"] = list(cast_info.values())
                title_info["aka"] = list(aka_info.values())
                title_info["episodes"] = episodes

                return title_info
            except Exception as e:
                print(f"Error fetching title for tconst {tconst}: {e}")
                return None
            
        elif data[0]['titleType'] == "movie":
            
            try:


                query = """
                SELECT 
                    tb.tconst,
                    tb.titleType,
                    tb.title,
                    tb.isAdult,
                    tb.startYear,
                    tb.endYear,
                    tb.genre,
                    tc.directorNconst,
                    director.originalName AS directorName,
                    tc.writerNconst,
                    writer.originalName AS writerName,
                    tr.averageRating,
                    tr.numVotes,
                    te.seasonNumber,
                    te.episodeNumber,
                    ta.title AS akaTitle,
                    ta.country AS akaCountry,
                    ta.isOriginal AS akaIsOriginal,
                    tcst.nconst AS castNconst,
                    cast.originalName AS castName,
                    tcst.category AS castCategory,
                    tcst.characterName AS castCharacter
                FROM 
                    title_basics tb
                LEFT JOIN title_crew tc 
                    ON tb.tconst = tc.tconst
                LEFT JOIN name_basics director 
                    ON tc.directorNconst = director.nconst
                LEFT JOIN name_basics writer 
                    ON tc.writerNconst = writer.nconst
                LEFT JOIN title_rating tr 
                    ON tb.tconst = tr.tconst
                LEFT JOIN title_episode te 
                    ON tb.tconst = te.tconst
                LEFT JOIN title_akas ta 
                    ON tb.tconst = ta.tconst
                LEFT JOIN title_cast tcst 
                    ON tb.tconst = tcst.tconst
                LEFT JOIN name_basics cast 
                    ON tcst.nconst = cast.nconst
                WHERE tb.tconst = %s
                """
                
                cursor = mysql.connection.cursor()
                cursor.execute(query, (tconst,)) 
                data = cursor.fetchall()
                cursor.close()

                if not data:
                    return None 
                
                title_info = {
                    "tconst": data[0]['tconst'],
                    "title": data[0]['title'],
                    "title_type": data[0]['titleType'],
                    "is_adult": data[0]['isAdult'],
                    "start_year": data[0]['startYear'],
                    "end_year": data[0]['endYear'],
                    "genre": data[0]['genre'],
                    "director_name": data[0]['directorName'],
                    "writer_name": data[0]['writerName'],
                    "average_rating": data[0]['averageRating'],
                    "num_votes": data[0]['numVotes'],
                }

                cast_info = {}
                aka_info = {}

                for row in data:
                        
                    
                    cast_info[(row['castNconst'], row['castCategory'], row['castCharacter'])] = {
                        'nconst': row['castNconst'],
                        'original_name': row['castName'],
                        'category': row['castCategory'],
                        'character_name': row['castCharacter'],  # Remove any trailing whitespace
                    }

                    # Aka info, using a dictionary to remove duplicates
                    aka_info[(row['akaTitle'], row['akaCountry'], row['akaIsOriginal'])] = {
                        'aka_title': row['akaTitle'],
                        'aka_country': row['akaCountry'],
                        'aka_is_original': row['akaIsOriginal'],
                    }

                # Convert the dictionaries back to lists
                title_info["cast"] = list(cast_info.values())
                title_info["aka"] = list(aka_info.values())
                return title_info

            except Exception as e:
                print(f"Error fetching title for tconst {tconst}: {e}")
                return None
