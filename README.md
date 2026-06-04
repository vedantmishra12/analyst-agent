# AI Data Analyst Agent

A locally-hosted AI analyst agent that lets you query uploaded datasets using natural language.

## Features
- Upload CSV, Excel, or Parquet files
- Ask questions in plain English — powered by LLaMA 3 via Ollama
- DuckDB-powered SQL execution under the hood
- Polars for fast in-memory processing
- Fully containerized with Docker

## Run Locally

**Prerequisites:** Docker installed

```bash
docker-compose up --build
```

Then open http://localhost:8501

Pull the model in a separate terminal:
```bash
docker exec -it ollama ollama pull llama3
```
