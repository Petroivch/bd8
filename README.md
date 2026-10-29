# Домашнее задание по защите баз данных

Проект демонстрирует три базовых механизма защиты PostgreSQL и MongoDB:

1. SQL-инъекцию в запросе, собранном конкатенацией строк, и защиту с помощью
   параметризации `psycopg2`;
2. разграничение прав в PostgreSQL: прикладному пользователю разрешён CRUD, но
   запрещено удалять таблицы;
3. обязательную аутентификацию MongoDB и отдельного пользователя приложения.

Демонстрация SQL-инъекции выполняет только обход учебной проверки пароля. Она
не удаляет и не изменяет таблицы.

## Структура проекта

```text
postgres/init/01_security_setup.sql  # роли, таблица и GRANT/REVOKE
mongo-init/01_create_app_user.js     # пользователь и тестовая коллекция MongoDB
sql_injection_demo.py                # сырой и параметризованный SQL
postgres_access_demo.py              # разрешённый CRUD и запрещённый DROP
mongodb_auth_demo.py                 # подключение без пароля и с паролем
main.py                              # запуск всех проверок
docker-compose.yml
```

## 1. SQL-инъекция и параметризация

Уязвимый вариант добавляет ввод прямо в текст SQL:

```python
query = (
    "SELECT id, username, role FROM accounts "
    f"WHERE username = '{username}' AND password = '{password}'"
)
cursor.execute(query)
```

Строка `admin' -- ` превращает оставшуюся проверку пароля в комментарий, и
неверный пароль больше не учитывается.

Безопасный вариант оставляет структуру SQL неизменной, а значения передаёт
драйверу отдельно:

```python
query = (
    "SELECT id, username, role FROM accounts "
    "WHERE username = %s AND password = %s"
)
cursor.execute(query, (username, password))
```

В этом случае вредоносная строка обрабатывается как обычное значение поля.

## 2. Права PostgreSQL

Объекты принадлежат роли `db_owner`, которая не может выполнять вход. Рабочая
роль `app_user` получает только:

- `CONNECT` для базы `db_security`;
- `USAGE` для схемы `public`;
- `SELECT`, `INSERT`, `UPDATE`, `DELETE` для таблицы `accounts`;
- `USAGE`, `SELECT` для identity-последовательности.

У `app_user` нет права `CREATE` для схемы и права владения таблицей. В
PostgreSQL выполнить `DROP TABLE` может владелец объекта или суперпользователь,
поэтому попытка удаления завершается ошибкой `InsufficientPrivilege`.

## 3. Аутентификация MongoDB

MongoDB запускается с root-пользователем, заданным переменными
`MONGO_INITDB_ROOT_USERNAME` и `MONGO_INITDB_ROOT_PASSWORD`. Инициализационный
скрипт создаёт отдельного пользователя `mongo_app` с ролью `readWrite` только
для базы `secure_app`.

Приложение не использует root-пользователя. Сценарий сначала пытается прочитать
коллекцию без пароля и получает код ошибки MongoDB `13` — Unauthorized. После
подключения как `mongo_app` чтение и запись разрешены.

## Запуск

Запустите обе базы данных:

```powershell
docker compose up -d
docker compose ps
```

Создайте виртуальное окружение и установите зависимости:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Запустите все три проверки:

```powershell
python main.py
```

Или запускайте сценарии отдельно:

```powershell
python sql_injection_demo.py
python postgres_access_demo.py
python mongodb_auth_demo.py
```

Ожидаемый смысл результата:

- сырой SQL ошибочно возвращает пользователя `admin`;
- параметризованный запрос с тем же вводом возвращает `None`;
- обычный параметризованный вход работает;
- `INSERT`, `UPDATE`, `DELETE` разрешены роли `app_user`;
- `DROP TABLE accounts` запрещён, таблица остаётся на месте;
- MongoDB отклоняет чтение без учётных данных;
- пользователь `mongo_app` может читать и изменять данные `secure_app`.

## Настройка подключения

Значения по умолчанию совпадают с `docker-compose.yml`. Для других адресов
используйте переменные окружения из `.env.example`:

```powershell
$env:POSTGRES_APP_DSN="postgresql://app_user:app_password@localhost:5432/db_security"
$env:MONGODB_UNAUTH_URI="mongodb://localhost:27017"
$env:MONGODB_APP_URI="mongodb://mongo_app:mongo_app_password@localhost:27017/secure_app?authSource=secure_app"
```

## Важно для реального проекта

Пароли в репозитории являются только локальными учебными значениями. В рабочей
среде их следует хранить в менеджере секретов или переменных окружения,
ограничить сетевой доступ к базам, включить TLS, регулярно обновлять зависимости
и хранить пароли пользователей приложения только в виде криптографических
хешей, например Argon2id или bcrypt.
