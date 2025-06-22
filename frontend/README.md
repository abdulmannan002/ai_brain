# AI Brain Vault - Frontend

This directory contains the Next.js frontend for the AI Brain Vault.

## Setup and Running

1.  **Navigate to the frontend directory:**
    ```bash
    cd ai_brain/frontend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Run the application:**
    ```bash
    npm run dev
    ```
    The application will start in development mode and be accessible at `http://localhost:3000/ideas`.

## Connecting to the Backend

The frontend is configured to proxy requests from `/api/...` to the backend service running at `http://localhost:8000`. This is handled by the `next.config.mjs` file. 