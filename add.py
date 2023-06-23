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

def main():
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    query = """
        INSERT INTO Access_logs (title_status_log, ip_address, request_time, request_path, status_code, response_size)
        VALUES ('Successful login', '192.168.0.1', '2023-06-22 15:30:00', '/login', 200, 1024);
    """
    cursor.execute(query)
    result = cursor.fetchall()