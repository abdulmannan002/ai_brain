# AI Brain Vault - Backend

This directory contains the FastAPI backend service for the AI Brain Vault.

## Setup and Running

1.  **Navigate to the backend directory:**
    ```bash
    cd ai_brain/backend
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up PostgreSQL:**
    Ensure you have a PostgreSQL server running. You can use Docker to easily run one:
    ```bash
    docker run --name postgres-aivault -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres
    ```
    Then, create the `ai_brain_vault` database.

5.  **Set environment variables:**
    ```bash
    export DB_USER=postgres
    export DB_PASSWORD=postgres
    export DB_HOST=localhost
    export DB_PORT=5432
    export DB_NAME=ai_brain_vault
    ```

6.  **Run the database schema:**
    Connect to your PostgreSQL instance and run the `database/schema.sql` script to create the tables.

7.  **Run the application:**
    ```bash
    uvicorn ai_brain_vault_service:app --reload
    ```
    The service will be available at `http://127.0.0.1:8000`. 