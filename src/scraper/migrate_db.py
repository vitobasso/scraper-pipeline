from src.common.services.repository import run_script

if __name__ == "__main__":
    run_script("resources/sql-schema/schema.sql")
    run_script("resources/sql-schema/seed_data.sql")
    # run_script("resources/sql-schema/migrate.sql")
