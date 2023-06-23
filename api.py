from datetime import datetime
import psycopg2
import json
from config import load_config
import random

# Загрузка конфигурации из файла
config = load_config()

# Конфигурация подключения к БД
db_config = {
    'dbname': config['database']['dbname'],
    'user': config['database']['username'],
    'password': config['database']['password'],
    'host': config['database']['host'],
    'port': config['database']['port']
}


def find_unique_ips():
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        query = "SELECT DISTINCT ip_address FROM access_logs"
        cursor.execute(query)
        result = cursor.fetchall()

        cursor.close()
        conn.close()

        # Получение только 5 случайных IP-адресов
        random_ips = random.sample(result, 5)
        ip_addresses = [ip[0] for ip in random_ips]

        # Преобразование IP-адресов в строку, разделенную запятыми
        ips_str = ', '.join(ip_addresses)

        return ips_str

    except Exception as e:
        print(f"Error: {str(e)}")


def find_earliest_date():
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        query = "SELECT MIN(request_time) FROM access_logs"
        cursor.execute(query)
        result = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return result

    except Exception as e:
        print(f"Error: {str(e)}")


def find_latest_date():
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        query = "SELECT MAX(request_time) FROM access_logs"
        cursor.execute(query)
        result = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return result

    except Exception as e:
        print(f"Error: {str(e)}")


def get_logs(start_date_str, end_date_str, ip_address):
    try:
        # Установка соединения с БД
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Подготовка и выполнение SQL-запроса с использованием параметров
        query = """
            SELECT * FROM access_logs
            WHERE request_time >= %s AND request_time <= %s
            AND (%s IS NULL OR ip_address = %s)
        """
        cursor.execute(query, (start_date_str, end_date_str, ip_address, ip_address))
        records = cursor.fetchall()

        # Проверка, возвращаются ли записи из базы данных
        if not records:
            return {'error': 'No records found.'}

        # Формирование списка словарей с результатами
        results = []
        for record in records:
            if isinstance(record[3], str):
                request_time = datetime.strptime(record[3], '%Y-%m-%d %H:%M:%S')
            else:
                request_time = record[3]
            result = {
                'ID': record[0],
                'title_status_log': record[1],
                'ip_address': record[2],
                'request_time': request_time.strftime('%Y-%m-%d %H:%M:%S'),
                'request_path': record[4],
                'status_code': record[5],
                'response_size': record[6]
            }
            results.append(result)

        # Закрытие соединения с БД
        cursor.close()
        conn.close()

        return results

    except Exception as e:
        return {'error': str(e)}


def input_data():
    start = input('Напишите начальную дату (YYYY-MM-DD) или ничего если не хотите по дате: ')
    end = ''

    if start.strip() == '':
        start = find_earliest_date()
        end = find_latest_date()
    else:
        end = input('Напишите конечную дату (YYYY-MM-DD) или ничего если до конечной: ')

    IP = input('Напишите IP (если хотите фильтровать по IP): ')

    if str(end).strip() == '':
        end = find_latest_date()

    if IP.strip() == '':
        IP = None

    return [start, end, IP]


def get_result(logs):
    with open('src/outputs/result.json', 'w') as file:
        json.dump(logs, file, indent=4)


def main():
    print('Самая ранняя дата:', find_earliest_date())
    print('Самая поздняя дата:', find_latest_date())
    print('Все виды IP:', find_unique_ips(), '\n')

    data = input_data()
    start_date = data[0]
    end_date = data[1]
    ip_log = data[2]

    logs = get_logs(start_date, end_date, ip_log)
    get_result(logs)


if __name__ == "__main__":
    main()
