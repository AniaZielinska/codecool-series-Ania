from data import data_manager


def get_shows():
    return data_manager.execute_select('SELECT id, title FROM shows;')


def get_most_rated_shows(page_num=1):
    return data_manager.execute_select("""
        SELECT title, 
               TO_CHAR(year, 'YYYY') AS year, 
               runtime,
               ROUND(rating, 2) AS rating, 
               COALESCE(trailer, 'No URL') AS trailer,
               STRING_AGG(genres.name, ', ') AS genres, 
               homepage FROM shows
        LEFT JOIN show_genres ON shows.id = show_genres.show_id
        LEFT JOIN genres ON genres.id = show_genres.genre_id
        GROUP BY shows.id
        ORDER BY shows.rating DESC
        OFFSET (%(page_num)s-1)*15 LIMIT 15;
        """, {'page_num': page_num})


def get_pages_num():
    return data_manager.execute_select("""
        SELECT count(*)/15 AS num FROM shows
        """, fetchall=False)
