import re
import time
from datetime import datetime
import psycopg2

start_time = time.time()

access_log_pattern = re.compile(r'^(\S+) \S+ \S+ \[(.*?)] "(GET|POST) (.*?) HTTP/1\.[01]" (\d+) (\d+) "(.*?)" "(.*?)"$')
access_success_pattern = re.compile(r'^(\S+) \S+ \S+ \[(.*?)] "(GET|POST) (.*?) HTTP/1\.[01]" 200 (\d+)$')
access_failure_pattern = re.compile(r'^(\S+) \S+ \S+ \[(.*?)] "(GET|POST) (.*?) HTTP/1\.[01]" 4\d{2} (\d+)$')
tortoise_svn_pattern = re.compile(r'^(\S+) \S+ \S+ \[(.*?)] "(PROPFIND|CHECKOUT) (.*?) HTTP/1\.[01]" 401 (\d+)$')


def access_log(title, ip, timestamp, http, url, status_code, response_size):
    output = {
        'Title': title,
        'IP': ip,
        'Timestamp': timestamp,
        'Method': http,
        'URL': url,
        'Status': status_code,
        'Response': response_size
    }
    return output


try:
    # Подключение к базе данных
    conn = psycopg2.connect(dbname='Practice', user='postgres', password='0909', host='127.0.0.1')
    conn.autocommit = True
    cursor = conn.cursor()

    # Подготовка подготовленного запроса для вставки данных
    insert_query = """
        INSERT INTO Access_logs (title_status_log, ip_address, request_time, request_path, status_code, response_size)
        SELECT %s, %s, %s, %s, %s, %s
        WHERE NOT EXISTS (
            SELECT 1 FROM Access_logs
            WHERE title_status_log = %s
                AND ip_address = %s
                AND request_time = %s
                AND request_path = %s
                AND status_code = %s
                AND response_size = %s
        )
    """

    with open('../../log/logs.log') as f:
        not_format_logs = f.readlines()

    logs = [line for line in not_format_logs]

    access_logs = []
    for log in logs:
        if match := access_success_pattern.match(log):
            access_logs.append(access_log("Apache access log (success - code 200):", match.group(1), match.group(2),
                                          match.group(3), match.group(4), '200',
                                          match.group(5)))

        elif match := access_log_pattern.match(log):
            access_logs.append(access_log("Apache access log:", match.group(1), match.group(2),
                                          match.group(3), match.group(4), match.group(5),
                                          match.group(6)))

        elif match := access_failure_pattern.match(log):
            access_logs.append(access_log("Apache access log (failure - code 4xx):", match.group(1),
                                          match.group(2), match.group(3), match.group(4), log.split()[-2],
                                          match.group(5)))

        elif match := tortoise_svn_pattern.match(log):
            access_logs.append(
                access_log("Apache unnacepted request methods (caused by TortoiseSVN):", match.group(1), match.group(2),
                           match.group(3), match.group(4),
                           log.split()[-2], match.group(5)))

    # Выполнение подготовленного запроса для каждой записи
    insert_data = [
        (item['Title'], item['IP'], datetime.strptime(item['Timestamp'], "%d/%b/%Y:%H:%M:%S %z"),
         item['URL'], int(item['Status']), int(item['Response']))
        for item in access_logs
    ]

    cursor.executemany(insert_query, insert_data)
    cursor.close()
    conn.close()

    loaded_logs = len(access_logs)  # Количество успешно загруженных логов

    print(f'Было успешно загружено {loaded_logs} новых логов')

except Exception as e:
    # В случае ошибки выводим сообщение об ошибке
    print("Произошла ошибка при загрузке логов в базу данных:")
    print(e)

end_time = time.time()

elapsed_time = end_time - start_time
print(f"Общее время затраченное на обработку всего файла: {elapsed_time} секунд")
