CREATE TABLE Access_logs (
    ID_logs serial not null CONSTRAINT PK_Logs PRIMARY KEY,
    title_status_log varchar(150) not null,
    ip_address varchar(255) not null,
    request_time timestamp not null,
    request_path VARCHAR(255) not null,
    status_code INT not null,
    response_size INT not null
);

CREATE TABLE Users (
    ID_Users serial not null CONSTRAINT PK_Users PRIMARY KEY,
    login VARCHAR not null constraint UQ_Login unique,
    password VARCHAR not null
);


CREATE INDEX idx_ip_address ON access_logs (ip_address);
CREATE INDEX idx_date_time ON access_logs (request_time);

select add_access_log('test2', 'test4', '2004-10-10 00:00:00-07:00', 'test', 'test', 10, 10);

select * from Access_logs;














-- insert into Users (login, password)
-- values ('admin', 'admin12345'),
--        ('first-lord15', '12345'),
--        ('user1', 'password1'),
--        ('user2', 'password2'),
--        ('user3', 'password3'),
--        ('user4', 'password4'),
--        ('user5', 'password5');


CREATE OR REPLACE FUNCTION add_access_log(p_title_status_log varchar(150), p_ip_address varchar(255), p_request_time timestamp,
 p_request_path varchar(255), p_status_code int, p_response_size int)
RETURNS VOID AS $$
BEGIN

    -- Вставка данных в таблицу
    INSERT INTO Access_logs (title_status_log, ip_address, request_time, request_path, status_code, response_size)
    VALUES (p_title_status_log, p_ip_address, p_request_time, p_request_path, p_status_code, p_response_size);

    -- Вывод сообщения об успешной вставке
    RAISE NOTICE 'Access log added successfully';
END;
$$ LANGUAGE plpgsql;

SELECT add_access_log('test', 'test2', '2004-10-10 00:00:00', 'test', 10, 10);
Select * from Access_logs