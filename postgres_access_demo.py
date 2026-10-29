"""Проверка ограниченных прав прикладного пользователя PostgreSQL."""

from __future__ import annotations

import psycopg2
from psycopg2 import errors

from config import POSTGRES_APP_DSN


def run_postgres_access_demo() -> None:
    """Проверить разрешённый DML и запрещённый DROP TABLE."""
    db_connection = psycopg2.connect(POSTGRES_APP_DSN)
    try:
        with db_connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO accounts (username, password, role) "
                "VALUES (%s, %s, %s) RETURNING id",
                ("permission_test", "temporary_password", "user"),
            )
            test_id = cursor.fetchone()[0]
            cursor.execute(
                "UPDATE accounts SET role = %s WHERE id = %s",
                ("updated_user", test_id),
            )
            cursor.execute("DELETE FROM accounts WHERE id = %s", (test_id,))
        db_connection.commit()
        print("=== POSTGRESQL: ПРАВА ДОСТУПА ===")
        print("INSERT, UPDATE и DELETE: разрешены")

        try:
            with db_connection.cursor() as cursor:
                cursor.execute("DROP TABLE accounts")
            db_connection.commit()
            raise AssertionError("DROP TABLE неожиданно выполнился")
        except errors.InsufficientPrivilege as error:
            db_connection.rollback()
            print("DROP TABLE: запрещён")
            print("Причина:", error.diag.message_primary)

        with db_connection.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM accounts")
            accounts_count = cursor.fetchone()[0]
        print("Таблица сохранилась, записей:", accounts_count)
        assert accounts_count >= 2
    finally:
        db_connection.close()


if __name__ == "__main__":
    run_postgres_access_demo()
