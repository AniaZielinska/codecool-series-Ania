from data import data_manager


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


def get_pages_num():
    return data_manager.execute_select("""
        SELECT count(*)/15 AS num FROM shows
        """, fetchall=False)
