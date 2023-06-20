import re
from datetime import datetime
# import psycopg2

logs = []
f = open('../../Logs.log')
NotFormatLogs = f.readlines()
for line in NotFormatLogs:
    logs.append(line)

result = []

access_log_pattern = r'^(\S+) \S+ \S+ \[(.*?)\] "(GET|POST) (.*?) HTTP/1\.[01]" (\d+) (\d+) "(.*?)" "(.*?)"$'
access_success_pattern = r'^(\S+) \S+ \S+ \[(.*?)\] "(GET|POST) (.*?) HTTP/1\.[01]" 200 (\d+)$'
access_failure_pattern = r'^(\S+) \S+ \S+ \[(.*?)\] "(GET|POST) (.*?) HTTP/1\.[01]" 4\d{2} (\d+)$'
tortoise_svn_pattern = r'^(\S+) \S+ \S+ \[(.*?)\] "(PROPFIND|CHECKOUT) (.*?) HTTP/1\.[01]" 401 (\d+)$'
error_log_pattern = r'^\[(.*?)\] \[error\] \[client (.*?)\] (.*)$'
error_log_startup_pattern = r'^\[(.*?)\] \[(notice|warn)\] (.*)$'
error_log_shutdown_pattern = r'^\[(.*?)\] \[(notice)\] (caught SIGTERM, shutting down)$'
resource_unavailable_pattern = r'^\[(.*?)\] \[error\] \(11\)(Resource temporarily unavailable: fork: Unable to fork new process)$'

# пытаемся подключиться к базе данных
# conn = psycopg2.connect(dbname='Practice', user='postgres', password='0909', host='127.0.0.1')
# cursor = conn.cursor()


def access_log(title, ip, timestamp, http, url, status_code, response_size, referer=None, user_agent=None):
    date_format = "%d/%b/%Y:%H:%M:%S %z"
    date = datetime.strptime(timestamp, date_format)
    output = f'Title: {title}\nIP: {ip}\nTimestamp: {date}\n'
    output += f'Method: {http}\nURL: {url}\nStatus Code: {status_code}\nResponse Size: {response_size}\n'

    if referer is not None:
        output += f'Referer: {referer}\n'
    if user_agent is not None:
        output += f'User-Agent: {user_agent}\n'

    output += '_____________________________________________________\n'
    return output


def message_log(title, timestamp, ip=None, type_message=None, message=None):
    date_format = "%a %b %d %H:%M:%S %Y"
    date = datetime.strptime(timestamp, date_format)
    output = f'Title: {title}\nClient IP: {ip}\nTimestamp: {date}\n'

    if type_message == 1:
        output += f'Error Message: {message}\n'
    elif type_message == 2:
        output += f'Log Message: {message}\n'
    else:
        output += f'Message: {message}\n'

    output += '_____________________________________________________\n'
    return output


for log in logs:
    if re.match(access_success_pattern, log):
        match = re.match(access_success_pattern, log)
        result.append(access_log("Apache access log (success - code 200):", match.group(1), match.group(2),
                                 match.group(3), match.group(4), '200', match.group(5)))

    elif re.match(access_log_pattern, log):
        match = re.match(access_log_pattern, log)
        result.append(access_log("Apache access log:", match.group(1), match.group(2), match.group(3),
                                 match.group(4), match.group(5), match.group(6), match.group(7), match.group(8)))

        # cursor.execute(f"Select add_access_log(\'Apache access log', "
        #                f"\'{match.group(1)}', '{match.group(2)}', "
        #                f"\'{match.group(3)}', '{match.group(4)}', "
        #                f"\'{match.group(5)}', {match.group(6)})")
        #
        # print('Nice')

    elif re.match(access_failure_pattern, log):
        match = re.match(access_failure_pattern, log)
        result.append(
            access_log("Apache access log (failure - code 4xx):", match.group(1), match.group(2), match.group(3),
                       match.group(4), log.split()[-2], match.group(5)))

    elif re.match(tortoise_svn_pattern, log):
        match = re.match(tortoise_svn_pattern, log)
        result.append(
            access_log("Apache unnacepted request methods (caused by TortoiseSVN):", match.group(1), match.group(2),
                       match.group(3),
                       match.group(4), log.split()[-2], match.group(5)))

    elif re.match(error_log_pattern, log):
        match = re.match(error_log_pattern, log)
        result.append(message_log("Apache error log:", match.group(1), match.group(2), 1, match.group(3)))

    elif re.match(error_log_shutdown_pattern, log):
        match = re.match(error_log_shutdown_pattern, log)
        result.append(
            message_log("Apache error log (shutdown by TERM signal):", match.group(1), None, 3, match.group(3)))

    elif re.match(error_log_startup_pattern, log):
        match = re.match(error_log_startup_pattern, log)
        result.append(message_log("Apache error log (startup):", match.group(1), None, 3, match.group(3)))

    elif re.match(resource_unavailable_pattern, log):
        match = re.match(resource_unavailable_pattern, log)
        result.append(message_log("Apache without resources:", match.group(1), None, 3, match.group(2)))
    else:
        result.append("Неизвестный тип лога")
        result.append('_____________________________________________________\n')

f = open('../../result.txt', 'w')

for log in result:
    f.write(log)

f.close()
# cursor.close()  # закрываем курсор
# conn.close()  # закрываем соединение
