
# Dispatch Management System

## Overview

This is a FastAPI-based application designed to manage dispatch and authentication operations. It supports user authentication, dispatch creation, and various dispatch management features including filtering, accepting, starting, and completing dispatches. The application is built with SQLAlchemy for database interactions and JWT for authentication.

## Features

- **User Authentication**: Sign up and login functionality with JWT token-based authentication.
- **Dispatch Management**: Create, accept, start, and complete dispatches.
- **Filtering**: Retrieve dispatches with filters for status, date, and area.
- **Pagination**: Supports pagination for dispatch listings.

## Technologies Used

- **FastAPI**: Web framework for building APIs.
- **SQLAlchemy**: ORM for database interactions.
- **PostgreSQL**: Database management system.
- **JWT**: JSON Web Tokens for authentication.
- **Pydantic**: Data validation and settings management using Python type annotations.
- **Alembic**: Database migration tool for SQLAlchemy.

## Project Structure

The project is organized as follows:

```
FASTAPI-USERS-DISPATCH-FINAL/
│
├── routers/
│   ├── __init__.py
│   ├── auth.py
│   ├── auth_bearer.py
│   ├── dispatch.py
│   └── auth_handler.py
│
├── auth_helper.py
├── database.py
├── crud.py
├── main.py
├── models.py
├── schemas.py
└── requirements.txt
```

- **`routers/`**: Contains route handlers and authentication-related files.
  - `__init__.py`: Initializes the `routers` package.
  - `auth.py`: Handles authentication routes.
  - `auth_bearer.py`: Manages token verification and bearer authentication.
  - `dispatch.py`: Manages dispatch-related routes.
  - `auth_handler.py`: Contains helper functions for authentication.
  
- **`auth_helper.py`**: Contains helper functions related to authentication.

- **`database.py`**: Manages database connections and configurations.

- **`crud.py`**: Contains CRUD operations for interacting with the database.

- **`main.py`**: The main entry point for the FastAPI application.

- **`models.py`**: Defines SQLAlchemy models.

- **`schemas.py`**: Defines Pydantic schemas for request and response validation.

- **`requirements.txt`**: Lists the dependencies for your project.

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/dispatch-management-system.git
   cd dispatch-management-system
   ```

2. **Set Up a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the Database**

   Ensure you have PostgreSQL installed and create a database. Update the database URL in `database.py` or `.env` file.

5. **Run Migrations**

   ```bash
   alembic upgrade head
   ```

6. **Start the Application**

   ```bash
   uvicorn main:app --reload
   ```

   Access the API at `http://127.0.0.1:8000`.

## Usage

### Authentication

- **Sign Up**

  `POST /api/auth/signup`

  Request Body:
  ```json
  {
    "username": "yourusername",
    "email": "youremail@example.com",
    "password": "yourpassword"
  }
  ```

- **Login**

  `POST /api/auth/login`

  Request Body:
  ```json
  {
    "email": "youremail@example.com",
    "password": "yourpassword"
  }
  ```

  Response:
  ```json
  {
    "jwt_token": "your_jwt_token",
    "token_type": "bearer"
  }
  ```

### Dispatch Management

- **Create Dispatch**

  `POST /dispatches/create`

  Request Body:
  ```json
  {
    "area": "some area"
  }
  ```

- **Retrieve Dispatches**

  `GET /dispatches`

  Query Parameters:
  - `page`: Page number (default: 1)
  - `limit`: Number of items per page (default: 10)

- **Filter Dispatches**

  `GET /dispatches/filter`

  Query Parameters:
  - `status`: Dispatch status (optional)
  - `date`: Dispatch date (optional, format: yyyy-mm-ddTHH:MM:SSZ)
  - `area`: Dispatch area (optional)
  - `page`: Page number (default: 1)
  - `limit`: Number of items per page (default: 10)

- **Accept Dispatch**

  `POST /dispatches/{dispatch_id}/accept`

- **Start Dispatch**

  `POST /dispatches/{dispatch_id}/start`

- **Complete Dispatch**

  `POST /dispatches/{dispatch_id}/complete`

  Request Body:
  ```json
  {
    "podImage(optional)": "url_to_image",
    "notes": "some notes",
    "recipientName": "recipient name"
  }
  ```

## Alembic Commands

Alembic is used for handling database migrations in this project. Here are some common commands:

- **Create a New Migration**:

  ```bash
  alembic revision --autogenerate -m "Migration message"
  ```

  This command generates a new migration script by comparing the current state of the models and the database schema.

- **Apply Migrations**:

  ```bash
  alembic upgrade head
  ```

  This applies all the pending migrations to the database, bringing it up to date.

- **Revert Migrations**:

  ```bash
  alembic downgrade -1
  ```

  This reverts the last migration. Use specific revision IDs to downgrade to a particular migration.

- **View Current Revision**:

  ```bash
  alembic current
  ```

  This shows the current version of the database.

## PostgreSQL Commands

PostgreSQL is the database system used in this project. Here are some essential commands:

- **Start PostgreSQL Service**:

  ```bash
  sudo service postgresql start
  ```

- **Stop PostgreSQL Service**:

  ```bash
  sudo service postgresql stop
  ```

- **Access PostgreSQL Command Line Interface**:

  ```bash
  psql -U yourusername -d yourdatabase
  ```

- **Create a Database**:

  ```sql
  CREATE DATABASE yourdatabase;
  ```

- **Create a User**:

  ```sql
  CREATE USER yourusername WITH PASSWORD 'yourpassword';
  ```

- **Grant Privileges**:

  ```sql
  GRANT ALL PRIVILEGES ON DATABASE yourdatabase TO yourusername;
  ```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes.
4. Push to the branch.
5. Create a Pull Request.

Please ensure your code adheres to the project's coding standards and includes appropriate tests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or issues, please open an issue on GitHub or contact [hafsashakeel@gmail.com](mailto:hafsashakeel@gmail.com).
```

