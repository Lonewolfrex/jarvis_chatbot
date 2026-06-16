from db_manager import DatabaseManager

db = DatabaseManager()

db.insert_finding(
    run_id=123,
    tool="Bandit",
    severity="HIGH",
    title="Use of eval()"
)

print("Inserted successfully")

db.close()