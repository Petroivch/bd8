"""Последовательный запуск всех демонстраций задания."""

from mongodb_auth_demo import run_mongodb_auth_demo
from postgres_access_demo import run_postgres_access_demo
from sql_injection_demo import run_sql_injection_demo


def main() -> None:
    run_sql_injection_demo()
    print()
    run_postgres_access_demo()
    print()
    run_mongodb_auth_demo()


if __name__ == "__main__":
    main()
