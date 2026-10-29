"""Сравнение уязвимого SQL-запроса и безопасной параметризации."""

from __future__ import annotations

from typing import Any

import psycopg2
from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor

from config import POSTGRES_APP_DSN


def vulnerable_login(
    db_connection: connection,
    username: str,
    password: str,
) -> tuple[dict[str, Any] | None, str]:
    """Небезопасный пример: пользовательский ввод склеивается с SQL."""
    query = (
        "SELECT id, username, role FROM accounts "
        f"WHERE username = '{username}' AND password = '{password}'"
    )
    with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(query)
        row = cursor.fetchone()
    return (dict(row) if row else None), query


def safe_login(
    db_connection: connection,
    username: str,
    password: str,
) -> dict[str, Any] | None:
    """Безопасный пример: значения передаются драйверу отдельно от SQL."""
    query = (
        "SELECT id, username, role FROM accounts WHERE username = %s AND password = %s"
    )
    with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(query, (username, password))
        row = cursor.fetchone()
    return dict(row) if row else None


def run_sql_injection_demo() -> None:
    """Показать обход проверки пароля и блокировку той же строки параметрами."""
    malicious_username = "admin' -- "
    incorrect_password = "wrong_password"

    with psycopg2.connect(POSTGRES_APP_DSN) as db_connection:
        vulnerable_result, raw_query = vulnerable_login(
            db_connection,
            malicious_username,
            incorrect_password,
        )
        safe_result = safe_login(
            db_connection,
            malicious_username,
            incorrect_password,
        )
        normal_result = safe_login(
            db_connection,
            "student",
            "student_demo_password",
        )

    print("=== SQL-ИНЪЕКЦИЯ ===")
    print("Вредоносный ввод:", repr(malicious_username))
    print("Сформированный сырой SQL:", raw_query)
    print("Результат сырого SQL:", vulnerable_result)
    print("Результат параметризованного SQL:", safe_result)
    print("Обычный вход с параметризацией:", normal_result)

    assert vulnerable_result is not None
    assert vulnerable_result["username"] == "admin"
    assert safe_result is None
    assert normal_result is not None


if __name__ == "__main__":
    run_sql_injection_demo()
