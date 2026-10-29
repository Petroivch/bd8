-- Роли разделены: db_owner владеет объектами, app_user работает только с данными.
DO
$$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'db_owner') THEN
        CREATE ROLE db_owner NOLOGIN;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_user') THEN
        CREATE ROLE app_user LOGIN PASSWORD 'app_password';
    END IF;
END
$$;

-- Подключаться к учебной базе может только явно разрешённая роль.
REVOKE ALL ON DATABASE db_security FROM PUBLIC;
GRANT CONNECT ON DATABASE db_security TO app_user;

-- Запрещаем обычным пользователям создавать объекты в общей схеме.
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO app_user;

CREATE TABLE IF NOT EXISTS accounts (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username varchar(100) NOT NULL UNIQUE,
    password varchar(100) NOT NULL,
    role varchar(50) NOT NULL
);

INSERT INTO accounts (username, password, role)
VALUES
    ('admin', 'admin_demo_password', 'administrator'),
    ('student', 'student_demo_password', 'user')
ON CONFLICT (username) DO NOTHING;

ALTER TABLE accounts OWNER TO db_owner;

REVOKE ALL ON TABLE accounts FROM PUBLIC;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE accounts TO app_user;
GRANT USAGE, SELECT ON SEQUENCE accounts_id_seq TO app_user;

-- app_user не является владельцем таблицы и не получает CREATE в public,
-- поэтому DROP TABLE и создание новых объектов для него недоступны.
