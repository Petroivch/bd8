const appDb = db.getSiblingDB("secure_app");

appDb.createUser({
  user: "mongo_app",
  pwd: "mongo_app_password",
  roles: [{ role: "readWrite", db: "secure_app" }],
});

appDb.secure_notes.createIndex({ owner: 1, created_at: -1 });

appDb.secure_notes.insertMany([
  {
    _id: "note-001",
    owner: "student",
    title: "Проверка аутентификации",
    body: "Документ доступен только после входа в MongoDB.",
    created_at: new Date("2026-10-20T10:00:00Z"),
    metadata: { category: "security", tags: ["mongodb", "auth"] },
  },
  {
    _id: "note-002",
    owner: "student",
    title: "Разделение пользователей",
    body: "Приложение не использует учётную запись root.",
    created_at: new Date("2026-10-21T12:00:00Z"),
    metadata: { category: "security", tags: ["roles", "least-privilege"] },
  },
]);
