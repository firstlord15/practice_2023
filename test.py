import re
from datetime import datetime, timezone, timedelta

logs = [
    '192.168.2.20 - - [28/Jul/2006:10:27:10 -0300] "GET /cgi-bin/try/ HTTP/1.0" 200 3395',
    '127.0.0.1 - - [28/Jul/2006:10:22:04 -0300] "GET / HTTP/1.0" 200 2216',
    '83.149.9.216 - - [17/May/2015:10:05:03 +0000] "GET /presentations/logstash-monitorama-2013/images/kibana-search.png HTTP/1.1" 200 203023 "http://semicomplete.com/presentations/logstash-monitorama-2013/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36"',

    '127.0.0.1 - - [28/Jul/2006:10:27:32 -0300] "GET /hidden/ HTTP/1.0" 404 7218',

    '192.168.2.90 - - [13/Sep/2006:07:01:53 -0700] "PROPFIND /svn/[xxxx]/Extranet/branches/SOW-101 HTTP/1.1" 401 587',
    'x.x.x.90 - - [13/Sep/2006:07:01:51 -0700] "PROPFIND /svn/[xxxx]/[xxxx]/trunk HTTP/1.1" 401 587',
    'x.x.x.90 - - [13/Sep/2006:07:00:53 -0700] "PROPFIND /svn/[xxxx]/[xxxx]/2.5 HTTP/1.1" 401 587',
    'x.x.x.90 - - [13/Sep/2006:07:00:53 -0700] "PROPFIND /svn/[xxxx]/Extranet/branches/SOW-101 HTTP/1.1" 401 587',
    'x.x.x.90 - - [13/Sep/2006:07:00:21 -0700] "PROPFIND /svn/[xxxx]/[xxxx]/trunk HTTP/1.1" 401 587',
    'x.x.x.90 - - [13/Sep/2006:06:59:53 -0700] "PROPFIND /svn/[xxxx]/[xxxx]/2.5 HTTP/1.1" 401 587',
    'x.x.x.90 - - [13/Sep/2006:06:59:50 -0700] "PROPFIND /svn/[xxxx]/[xxxx]/trunk HTTP/1.1" 401 587',
    'x.x.x.90 - - [13/Sep/2006:06:58:52 -0700] "PROPFIND /svn/[xxxx]/[xxxx]/trunk HTTP/1.1" 401 587',
    '213.312.213.90 - - [13/Sep/2006:06:58:52 -0700] "PROPFIND /svn/[xxxx]/Extranet/branches/SOW-101 HTTP/1.1" 401 587',

    '[Fri Dec 16 01:46:23 2005] [error] [client 1.2.3.4] Directory index forbidden by rule: /home/test/',
    '[Fri Dec 16 01:54:34 2005] [error] [client 1.2.3.4] Directory index forbidden by rule: /apache/web-data/test2',
    '[Fri Dec 16 02:25:55 2005] [error] [client 1.2.3.4] Client sent malformed Host header',
    '[Mon Dec 19 23:02:01 2005] [error] [client 1.2.3.4] user test: authentication failure for "/~dcid/test1": Password Mismatch',

    '[Sat Aug 12 04:05:51 2006] [notice] Apache/1.3.11 (Unix) mod_perl/1.21 configured -- resuming normal operations',
    '[Thu Jun 22 14:20:55 2006] [notice] Digest: generating secret for digest authentication ...',
    '[Thu Jun 22 14:20:55 2006] [notice] Digest: done',
    '[Thu Jun 22 14:20:55 2006] [notice] Apache/2.0.46 (Red Hat) DAV/2 configured -- resuming normal operations',
    '[Sat Jun 24 09:06:22 2006] [warn] pid file /opt/CA/BrightStorARCserve/httpd/logs/httpd.pid overwritten -- Unclean shutdown of previous Apache run?',
    '[Sat Jun 24 09:06:23 2006] [notice] Apache/2.0.46 (Red Hat) DAV/2 configured -- resuming normal operations',
    '[Sat Jun 24 09:06:22 2006] [notice] Digest: generating secret for digest authentication ...',
    '[Sat Jun 24 09:06:22 2006] [notice] Digest: done',

    '[Thu Jun 22 11:35:48 2006] [notice] caught SIGTERM, shutting down',
    '[Sat Jun 24 09:06:22 2006] [notice] caught SIGTERM, shutting down',

    '[Tue Mar 08 10:34:21 2005] [error] (11)Resource temporarily unavailable: fork: Unable to fork new process',
    '[Tue Mar 08 10:34:31 2005] [error] (11)Resource temporarily unavailable: fork: Unable to fork new process'
]

result = []

access_log_pattern = r'^(\S+) \S+ \S+ \[(.*?)\] "(GET|POST) (.*?) HTTP/1\.[01]" (\d+) (\d+) "(.*?)" "(.*?)"$'
access_success_pattern = r'^(\S+) \S+ \S+ \[(.*?)\] "(GET|POST) (.*?) HTTP/1\.[01]" 200 (\d+)$'
access_failure_pattern = r'^(\S+) \S+ \S+ \[(.*?)\] "(GET|POST) (.*?) HTTP/1\.[01]" 4\d{2} (\d+)$'
tortoise_svn_pattern = r'^(\S+) \S+ \S+ \[(.*?)\] "(PROPFIND|CHECKOUT) (.*?) HTTP/1\.[01]" 401 (\d+)$'
error_log_pattern = r'^\[(.*?)\] \[error\] \[client (.*?)\] (.*)$'
error_log_startup_pattern = r'^\[(.*?)\] \[(notice|warn)\] (.*)$'
error_log_shutdown_pattern = r'^\[(.*?)\] \[(notice)\] (caught SIGTERM, shutting down)$'
resource_unavailable_pattern = r'^\[(.*?)\] \[error\] \(11\)(Resource temporarily unavailable: fork: Unable to fork new process)$'


def access_log(Title, IP, Timestamp, Http, Url, StatusCode, ResponseSize, referer=None, user_agent=None):
    if not (referer is None and user_agent is None):
        return f'Title: {Title}' \
               f'\nIP:, {IP}\nTimestamp: {Timestamp}' \
               f'\nMethod: {Http}\nURL: {Url}\nStatus Code: {StatusCode}\nResponse size: {ResponseSize}' \
               f'\nReferer: {referer}\nUser-Agent: {user_agent}\n' \
               '_____________________________________________________\n'
    else:
        return f'Title: {Title}' \
               f'\nIP:, {IP}\nTimestamp: {Timestamp}' \
               f'\nMethod: {Http}\nURL: {Url}\nStatus Code: {StatusCode}\nResponse size: {ResponseSize}\n' \
               '_____________________________________________________\n'


def message_log(Title, Timestamp, IP=None, Type_Message=None, Message=None):
    if Type_Message == 1:
        return f'Title: {Title}' \
               f'\nClient IP: {IP}\nTimestamp: {Timestamp}\n' \
               f'Error Message: {Message} \n' \
               '_____________________________________________________\n'
    elif Type_Message == 2:
        return f'Title: {Title}' \
               f'\nClient IP: {IP}\nTimestamp: {Timestamp}\n' \
               f'Log Message: {Message} \n' \
               '_____________________________________________________\n'

    else:
        return f'Title: {Title}' \
               f'\nClient IP: {IP}\nTimestamp: {Timestamp}\n' \
               f'Message: {Message} \n' \
               '_____________________________________________________\n'


for log in logs:
    if re.match(access_success_pattern, log):
        match = re.match(access_success_pattern, log)
        result.append(access_log("Apache access log (success - code 200):", match.group(1), match.group(2),
                                 match.group(3), match.group(4), '200', match.group(5)))

    elif re.match(access_log_pattern, log):
        match = re.match(access_log_pattern, log)
        result.append(access_log("Apache access log:", match.group(1), match.group(2), match.group(3),
                                 match.group(4), match.group(5), match.group(6), match.group(7), match.group(8)))

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

for log in result:
    print(log)
