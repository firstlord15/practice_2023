import psycopg2

try:
    # пытаемся подключиться к базе данных
    conn = psycopg2.connect(dbname='Practice', user='postgres', password='0909', host='127.0.0.1')
    cursor = conn.cursor()
    cursor.execute("SELECT add_access_log('test', 'test2', '2004-10-10 00:00:00', 'test', 'test', 10, 10)")
    conn.commit()
    cursor.execute("SELECT * from Access_logs")
    data = cursor.fetchall()

    for item in data:
        print(item)

    cursor.close()  # закрываем курсор
    conn.close()  # закрываем соединение
except Exception as e:
    # в случае сбоя подключения будет выведено сообщение в STDOUT
    print(e)
