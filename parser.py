from datetime import datetime
from config import db_config_main, LOGS_PATH
import psycopg2
import re

access_log_pattern = r'^(\S+) \S+ \S+ \[(.*?)\] "(GET|POST) (.*?) HTTP/1\.[01]" (\d+) (\d+) "(.*?)" "(.*?)"$'
access_success_pattern = r'^(\S+) \S+ \S+ \[(.*?)\] "(GET|POST) (.*?) HTTP/1\.[01]" 200 (\d+)$'
access_failure_pattern = r'^(\S+) \S+ \S+ \[(.*?)\] "(GET|POST) (.*?) HTTP/1\.[01]" 4\d{2} (\d+)$'
tortoise_svn_pattern = r'^(\S+) \S+ \S+ \[(.*?)\] "(PROPFIND|CHECKOUT) (.*?) HTTP/1\.[01]" 401 (\d+)$'


def access_log(title, ip, timestamp, method, url, status_code, response_size):
    output = {
        'Title': title,
        'IP': ip,
        'Timestamp': timestamp,
        'Method': method,
        'URL': url,
        'Status': status_code,
        'Response': response_size
    }
    return output


def main_func_parser():
    try:
        # Подключение к базе данных
        conn = psycopg2.connect(**db_config_main)
        conn.autocommit = True
        cursor = conn.cursor()

        # Подготовка подготовленного запроса для вставки данных
        insert_query = """
            INSERT INTO access_logs (log_id, title_status_log, ip_address, request_time, request_path, status_code, response_size)
            SELECT %s, %s, %s, %s, %s, %s, %s
            WHERE NOT EXISTS (
                SELECT 1 FROM access_logs
                WHERE log_id = %s
                    AND title_status_log = %s
                    AND ip_address = %s
                    AND request_time = %s
                    AND request_path = %s
                    AND status_code = %s
                    AND response_size = %s
            )
        """

        with open(LOGS_PATH) as f:
            not_format_logs = f.readlines()

        logs = [line for line in not_format_logs]

        access_logs = []
        for log in logs:

            if match := re.match(access_success_pattern, log):
                access_logs.append(access_log("Apache access log (success - code 200):", match.group(1), match.group(2),
                                              match.group(3), match.group(4), '200', match.group(5)))

            elif match := re.match(access_log_pattern, log):
                access_logs.append(access_log("Apache access log:", match.group(1), match.group(2),
                                              match.group(3), match.group(4), match.group(5),
                                              match.group(6)))

            elif match := re.match(access_failure_pattern, log):
                access_logs.append(access_log("Apache access log (failure - code 4xx):", match.group(1),
                                              match.group(2), match.group(3), match.group(4), log.split()[-2],
                                              match.group(5)))

            elif match := re.match(tortoise_svn_pattern, log):
                access_logs.append(
                    access_log("Apache unnacepted request methods (caused by TortoiseSVN):", match.group(1),
                               match.group(2),
                               match.group(3), match.group(4),
                               log.split()[-2], match.group(5)))

        # Выполнение подготовленного запроса для каждой записи
        insert_data = [
            (log_id, item['Title'], item['IP'], datetime.strptime(item['Timestamp'], "%d/%b/%Y:%H:%M:%S %z"),
             item['URL'], int(item['Status']), int(item['Response']), log_id,
             item['Title'], item['IP'], datetime.strptime(item['Timestamp'], "%d/%b/%Y:%H:%M:%S %z"),
             item['URL'], int(item['Status']), int(item['Response']))
            for log_id, item in enumerate(access_logs, start=1)
        ]

        cursor.executemany(insert_query, insert_data)
        cursor.close()
        conn.close()

        loaded_logs = cursor.rowcount

        if loaded_logs > 0:
            print(f'Было успешно загружено {loaded_logs} новых логов')
        else:
            print('Нет новых логов для загрузки')

    except Exception as e:
        # В случае ошибки выводим сообщение об ошибке
        print("Произошла ошибка при загрузке логов в базу данных:")
        print(e)


if __name__ == "__main__":
    main_func_parser()
