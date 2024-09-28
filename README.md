# AFRIVIA API

A Trivia API Service tailored to an african audience.

## Table of Contents

- [Description](#description)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Database Setup](#database-setup)
  - [Migrations](#migrations)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
  - [SQL Schema](#sql-schema)
  - [DBML](#dbml)
- [License](#license)

## Description

Afrivia is an API service built for the purpose of collecting and reviewing trivia questions on topics strictly related to the african continent.

## Features

- **FastAPI**: A modern, fast web framework for building APIs.
- **Alembic**: A lightweight database migration tool for SQLAlchemy.
- **SQL Schema**: A file representing the structure of your database.
- **DBML**: Database Markup Language (DBML) file for database design and visualization.

## Requirements

- Python 3.10+
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Arnthorny/afrivia.git
   cd afrivia
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Database Setup

### Migrations

The project uses Alembic for database migrations. To run migrations:

1. Initialize the database and run the migrations:

   ```bash
   alembic upgrade head
   ```

2. To create a new migration:

   ```bash
   alembic revision --autogenerate -m "your migration message"
   ```

3. Apply the new migration:

   ```bash
   alembic upgrade head
   ```

## Running the Application

1. Start the FastAPI server:

   ```bash
   uvicorn app.main:app --reload
   ```

2. The application will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).

3. Visit the interactive API documentation:

   - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Project Structure

```bash
afrivia/
│
├── alembic/ # Alembic migrations folder
│ ├── versions/
├── api/
│ ├── core/
│ ├── db/ # Database configuration
│ ├── utils/ # Helper functions
│ ├── v1
│   ├── models/ # Database models
│   ├── routes/ # FastAPI Routes folder
│   ├── schemas/ # Pydantic schemas
│   └── services/ # Service files
│
│
├── schema.sql # SQL schema file
├── schema.dbml
│
├── tests/ # Test cases
│ └── v1/
│
├── alembic.ini # Alembic configuration
├── requirements.txt # Python dependencies
├── main.py # FastAPI application entry point
├── pytest.ini # Pytest configuration
├── requirements.txt # Python dependencies
└── README.md # Project documentation
```

## Database Schema

### SQL Schema

The SQL schema file (`schema.sql`) defines the structure of the database. You can apply this schema to a database by running:

```bash
psql -U username -d yourdatabase -f sql/schema.sql
```

### DBML

The DBML file (`schema.dbml`) can be used to visualize and design the database schema. You can convert this file to SQL using the [DBML CLI](https://www.dbml.org/cli/).

To generate an SQL schema from the DBML file:

```bash
dbml2sql --input dbml/schema.dbml --output sql/schema.sql
```
