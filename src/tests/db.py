import psycopg2

try:
    try:
        # Подключение к PostgreSQL
        conn = psycopg2.connect(dbname='postgres', user='postgres', password='0909', host='127.0.0.1')
        cursor = conn.cursor()

        # Проверка наличия базы данных Practice
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='Practice'")
        database_exists = cursor.fetchone()

        if not database_exists:
            # Создание базы данных Practice
            cursor.execute("CREATE DATABASE Practice;")
            conn.commit()
            print("База данных Practice успешно создана.")
        else:
            print("База данных Practice уже существует.")

        cursor.close()
        conn.close()
    except Exception as e:
        print(e)

    # Подключение к базе данных Practice
    conn = psycopg2.connect(dbname='Practice', user='postgres', password='0909', host='127.0.0.1')
    cursor = conn.cursor()

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
        conn.commit()

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
        conn.commit()
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
        conn.commit()
        print("Функция add_access_log успешно создана.")
    else:
        print("Функция add_access_log уже существует.")

    # Завершение транзакции и закрытие соединения
    conn.commit()
    print('\n[Все готово!]')
    cursor.close()
    conn.close()

except Exception as e:
    # В случае сбоя подключения будет выведено сообщение об ошибке
    print(e)
