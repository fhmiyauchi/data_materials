set dotenv-load := true

# Display available commands
default:
    @just --list

# Format the code using ruff
format:
    ruff format src

# Lint the code using ruff
lint:
    ruff check src --fix

# Typecheck the code using mypy
typecheck:
    mypy src

# Download the datasets as CSVs
download *args:
    docker-compose run --rm --build importer python -m src.main --action download {{args}}

# Import downloaded CSVs to SQLite database
import:
    docker-compose run --rm --build importer python -m src.main --action import
