import psycopg2
from config import load_config

config = load_config()

db_config = {
    'dbname': config['database']['dbname'],
    'user': config['database']['username'],
    'password': config['database']['password'],
    'host': config['database']['host'],
    'port': config['database']['port']
}


def check_func():
    try:
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                # Проверка наличия базы данных Practice
                cursor.execute("SELECT 1 FROM pg_database WHERE datname='Practice'")
                database_exists = cursor.fetchone()

                if not database_exists:
                    # Создание базы данных Practice
                    cursor.execute("CREATE DATABASE Practice;")
                    print("База данных Practice успешно создана.")
                else:
                    print("База данных Practice уже существует.")

        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cursor:

                # Подключение к базе данных Practice
                cursor.execute("SET search_path TO Practice")  # Устанавливаем схему по умолчанию
                conn.commit()

                # Проверка наличия таблицы Access_logs
                cursor.execute("SELECT 1 FROM information_schema.tables WHERE table_name='access_logs'")
                access_logs_table_exists = cursor.fetchone()

                if not access_logs_table_exists:
                    # Создание таблицы Access_logs
                    cursor.execute("""
                        CREATE TABLE Access_logs (
                            log_id SERIAL PRIMARY KEY,
                            title_status_log TEXT NOT NULL,
                            ip_address TEXT NOT NULL,
                            request_time TIMESTAMP NOT NULL,
                            request_path TEXT NOT NULL,
                            status_code INTEGER NOT NULL,
                            response_size INTEGER NOT NULL
                        )
                    """)

                    print("Таблица Access_logs успешно создана.")
                else:
                    print("Таблица Access_logs уже существует.")

                # Проверка наличия таблицы Users
                cursor.execute("SELECT 1 FROM information_schema.tables WHERE table_name='users'")
                users_table_exists = cursor.fetchone()

                if not users_table_exists:
                    # Создание таблицы Users
                    cursor.execute("""
                        CREATE TABLE Users (
                            ID_Users serial not null CONSTRAINT PK_Users PRIMARY KEY,
                            login VARCHAR not null constraint UQ_Login unique,
                            password VARCHAR not null
                        );
                    """)
                    print("Таблица Users успешно создана.")
                else:
                    print("Таблица Users уже существует.")

                # Проверка наличия функции add_access_log
                cursor.execute("""
                    SELECT 1
                    FROM pg_proc
                    WHERE proname = 'add_access_log' AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
                """)
                add_access_log_function_exists = cursor.fetchone()

                if not add_access_log_function_exists:
                    # Определение функции add_access_log
                    cursor.execute("""
                        CREATE OR REPLACE FUNCTION add_access_log(
                            p_title_status_log varchar(150),
                            p_ip_address varchar(255),
                            p_request_time timestamp,
                            p_request_path varchar(255),
                            p_status_code int,
                            p_response_size int)
                        RETURNS VOID AS $$
                        BEGIN
                            -- Вставка данных в таблицу
                            INSERT INTO Access_logs (title_status_log, ip_address, request_time, request_path, status_code, response_size)
                            VALUES (p_title_status_log, p_ip_address, p_request_time, p_request_path, p_status_code, p_response_size);

                            -- Вывод сообщения об успешной вставке
                            RAISE NOTICE 'Access log added successfully';
                        END;
                        $$ LANGUAGE plpgsql;
                    """)
                    print("Функция add_access_log успешно создана.")
                else:
                    print("Функция add_access_log уже существует.")

                conn.commit()

        print('\n[Все готово!]')
    except Exception as e:
        print(e)

