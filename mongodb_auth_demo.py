"""Проверка базовой аутентификации MongoDB."""

from __future__ import annotations

from datetime import UTC, datetime

from pymongo import MongoClient
from pymongo.errors import OperationFailure

from config import MONGODB_APP_URI, MONGODB_UNAUTH_URI


def run_mongodb_auth_demo() -> None:
    """Показать отказ без пароля и доступ прикладного пользователя."""
    print("=== MONGODB: АУТЕНТИФИКАЦИЯ ===")

    with MongoClient(MONGODB_UNAUTH_URI, serverSelectionTimeoutMS=5_000) as client:
        try:
            client["secure_app"]["secure_notes"].find_one()
            raise AssertionError("Чтение без аутентификации неожиданно разрешено")
        except OperationFailure as error:
            assert error.code == 13
            print("Чтение без учётных данных: запрещено")
            print("Код MongoDB:", error.code)

    with MongoClient(MONGODB_APP_URI, serverSelectionTimeoutMS=5_000) as client:
        database = client["secure_app"]
        database.command("ping")
        notes = database["secure_notes"]

        initial_count = notes.count_documents({})
        demo_id = "temporary-auth-check"
        notes.replace_one(
            {"_id": demo_id},
            {
                "_id": demo_id,
                "owner": "student",
                "title": "Временная проверка",
                "body": "Запись создана прикладным пользователем.",
                "created_at": datetime.now(UTC),
                "metadata": {"category": "security", "tags": ["auth-check"]},
            },
            upsert=True,
        )
        created = notes.find_one({"_id": demo_id})
        notes.delete_one({"_id": demo_id})

        print("Вход как mongo_app: выполнен")
        print("Исходных документов:", initial_count)
        print("Создание и чтение документа:", "успешно" if created else "ошибка")
        print("Временный документ удалён:", notes.find_one({"_id": demo_id}) is None)

        assert initial_count >= 2
        assert created is not None


if __name__ == "__main__":
    run_mongodb_auth_demo()
