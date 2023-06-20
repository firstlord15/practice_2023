CREATE TABLE Access_logs (
    ID_logs serial not null CONSTRAINT PK_Logs PRIMARY KEY,
    title_status_log varchar(150) not null,
    ip_address varchar(255) not null,
    request_time timestamp not null,
    request_method VARCHAR(50) not null,
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