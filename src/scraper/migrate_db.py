from src.common.services import repository


def migrate():
    repository.run_script("resources/sql-schema/migrate.sql")


if __name__ == "__main__":
    migrate()
