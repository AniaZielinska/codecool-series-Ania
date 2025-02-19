from data_manager import ensure_var, get_connection_data, establish_connection


def init_db():
    # We need to connect to postgres db to be able to drop our db
    connection_data = get_connection_data('postgres')
    db_to_init = ensure_var('MY_PSQL_DBNAME')
    print(f'Running init with connection data: {connection_data} and initializing database: {db_to_init}')

    # Using `try` instead of `with`, because with psycopg 2.9, the connection starts a transaction if it's
    # put into a `with` block, but that would produce the following error:
    # ```
    # DROP DATABASE cannot run inside a transaction block
    # ```
    conn = establish_connection(connection_data=connection_data)
    try:
        with conn.cursor() as cursor:
            try:
                drop_statement = 'DROP DATABASE IF EXISTS "{}";'.format(db_to_init)
                create_statement = 'CREATE DATABASE "{}";'.format(db_to_init)
                cursor.execute(drop_statement)
                cursor.execute(create_statement)
                print(f"Database {db_to_init} is created")
            except Exception as ex:
                print(f"Database creation failed: {db_to_init}")
                raise(ex)
    finally:
        conn.close()


def create_schema():
    creation_script_file = 'data/db_schema/01_create_schema.sql'
    with open(creation_script_file) as schema_script:
        with establish_connection() as conn, \
                conn.cursor() as cursor:
            try:
                sql_to_run = schema_script.read()
                cursor.execute(sql_to_run)
                print("Database schema created")
            except Exception as ex:
                print("Schema creation failed")
                print(ex.args)
