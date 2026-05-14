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

# Start the EDA Apache Superset Dashboard
eda-up:
    docker-compose up -d superset superset-init

# Stop the EDA Apache Superset Dashboard
eda-down:
    docker-compose stop superset superset-redis superset-init

# Prepare the AI Layer (Feature Engineering + Embeddings)
ai-prepare:
    docker-compose run --rm --build importer python -m src.ai.build_ai_dataset
    docker-compose run --rm importer python -m src.ai.build_vector_store

# Test semantic retrieval
ai-test:
    docker-compose run --rm importer python -m src.ai.test_retrieval

# Run the AI Streamlit Dashboard
ai-up:
    docker-compose run --rm -p 8501:8501 importer streamlit run src/ai/app.py --server.port 8501 --server.address 0.0.0.0
