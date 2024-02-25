from data import data_manager
from math import trunc


def get_shows():
    return data_manager.execute_select('SELECT id, title FROM shows;')


def get_most_rated_shows(page_num=1, sort_column='rating', sort_direction='DESC'):
    valid_sort_columns = ['title', 'year', 'runtime', 'rating']

    if sort_column.lower() not in valid_sort_columns:
        sort_column = 'rating'

    if sort_direction.upper() not in ['ASC', 'DESC']:
        sort_direction = 'DESC'

    query = """
            SELECT title, 
                   TO_CHAR(year, 'YYYY') AS year, 
                   runtime,
                   ROUND(rating, 2) AS rating, 
                   COALESCE(trailer, 'No URL') AS trailer,
                   STRING_AGG(genres.name, ', ') AS genres, 
                   homepage 
            FROM shows
            LEFT JOIN show_genres ON shows.id = show_genres.show_id
            LEFT JOIN genres ON genres.id = show_genres.genre_id
            GROUP BY shows.id
            ORDER BY 
                CASE %(sort_column)s
                    WHEN 'title' THEN title::TEXT
                    WHEN 'year' THEN year::TEXT
                    WHEN 'runtime' THEN runtime::TEXT
                    ELSE rating::TEXT
                END """ + sort_direction + """
            OFFSET (%(page_num)s-1)*15 LIMIT 15;
    """
    params = {'page_num': page_num, 'sort_column': sort_column}
    return data_manager.execute_select(query, params)


def get_show_details(show_id):
    query = """
        SELECT actors.name AS actors FROM shows
        LEFT JOIN show_characters ON show_characters.show_id = shows.id
        LEFT JOIN actors ON actors.id = show_characters.actor_id
        WHERE shows.id = %(show_id)s
        LIMIT 3
    """
    actors = data_manager.execute_select(query, {'show_id': show_id})

    query = """
        SELECT title,
               runtime,
               ROUND(rating, 2) AS rating,
               STRING_AGG(genres.name, ', ') AS genres,
               overview,
               trailer
        FROM shows
        LEFT JOIN show_genres ON shows.id = show_genres.show_id
        LEFT JOIN genres ON genres.id = show_genres.genre_id
        WHERE shows.id = %(show_id)s
        GROUP BY shows.id
    """
    show_details = data_manager.execute_select(query, {'show_id': show_id}, fetchall=False)

    time_h, time_min = '', ''
    time = show_details['runtime']
    if time >= 60:
        time_h = str(trunc(time / 60)) + 'h'
    if time % 60 != 0:
        time_min = str(time % 60) + 'min'
    time = time_h + ' ' + time_min
    show_details['runtime'] = time

    show_actors = []
    for actor in actors:
        show_actors.append(actor['actors'])
    show_actors = ", ".join(show_actors)
    show_details['actors'] = show_actors

    return show_details


def get_pages_num():
    return data_manager.execute_select("""
        SELECT count(*)/15 AS num FROM shows
        """, fetchall=False)
