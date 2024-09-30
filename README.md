# OnHires DRF Test Task

This is a Django REST Framework (DRF) API server that provides endpoints to manage Wallet and Transaction models, complete with capabilities for pagination, sorting, and filtering. The project utilizes Python 3.12, Django, MySQL, and adheres to best practices in API development.


## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
    - [Using Docker (Recommended)](#using-docker-recommended)
- [Usage](#usage)
  - [API Endpoints](#api-endpoints)
    - [Wallets](#wallets)
    - [Transactions](#transactions)
    - [Notes](#notes)
  - [Swagger Documentation](#swagger-documentation)
  - [Pagination, Sorting, and Filtering](#pagination-sorting-and-filtering)
  - [Testing](#testing)
  - [Examples of API Requests with cURL](#examples-of-api-requests-with-curl)
- [Code Quality](#code-quality)
- [Quick Start with Docker](#quick-start-with-docker)
- [Project Structure](#project-structure)
- [Additional Notes](#additional-notes)
- [Admin Interface](#admin-interface)
- [Limitations](#limitations)
- [License](#license)

## Features

- Wallet Model: Represents a wallet with a label and balance.
- Transaction Model: Represents a transaction linked to a wallet, with unique transaction IDs and amounts (positive or negative).
- API Endpoints: CRUD operations for wallets and transactions.
- Pagination, Sorting, and Filtering: Built-in support for efficient data retrieval.
- Test Coverage: Comprehensive unit tests for models and API endpoints.
- Linters: Code quality enforced using ruff and black.
- Docker Integration: Quick start using Docker and Docker Compose.
- Database Indexes: Optimized queries with appropriate indexing.
- Commenting in Unconventional Places: Code includes comments in non-standard locations to explain complex logic.

## Requirements

- Python 3.12 or newer
- MySQL database
- Docker and Docker Compose (optional, for quick start)
- Poetry for dependency management

## Installation

### Using Docker (Recommended)

###### Tested on: MacOS Sequoia 15.0 (24A335) with Apple Silicon chip

1. Clone the Repository:

```bash
git clone git@github.com:oldevgeny/onhires-drf-test-task.git
cd onhires-drf-test-task
```

2. Set Up Environment Variables:

- Copy the example environment file and edit it:

```bash
cp .env.example .env.local
```

- Open .env.local and fill in all the environment variables:

```bash
vim .env.local
```

```bash
SECRET_KEY=django-INSECURE----=*n6^mc&7v0e-(^_dt6(b=e&pbq8bd55^az7@4u7!cafj3k
DB_NAME=mysql
DB_HOST=onhires_drf_test_task_db
DB_PORT=3306
DB_USER=root
DB_PASS=
```

3. Ensure Execution Permission for Entry Point Script:

```bash
chmod +x infra/entrypoint.sh
```

4. Build and Run the Containers:

```bash
make run
```

This command will:
- Build the Docker images.
- Start the containers for the web application and the database.
- Apply database migrations.

5. Access the API:
The API server will be running at http://localhost:8000/.


## Usage

Use the following command for help:

```bash
make help
```

### API Endpoints


#### Wallets
- List Wallets: GET /wallets/
- Retrieve a Wallet: GET /wallets/{id}/
- Create a Wallet: POST /wallets/
- Update a Wallet: PUT /wallets/{id}/
- Delete a Wallet: DELETE /wallets/{id}/

**Fields:**
- id: Auto-increment primary key.
- label: String field.
- balance: Non-negative numeric field.

#### Transactions
- List Transactions: GET /transactions/
- Retrieve a Transaction: GET /transactions/{id}/
- Create a Transaction: POST /transactions/
- Update a Transaction: PUT /transactions/{id}/
- Delete a Transaction: DELETE /transactions/{id}/

**Fields:**
- id: Auto-increment primary key.
- wallet: Foreign key to Wallet.
- txid: Unique string identifier.
- amount: Numeric field with 18-digit precision (can be negative).

#### Notes
- Creating or updating a transaction adjusts the associated wallet’s balance.
- Wallet balance cannot be negative. Transactions that would result in a negative balance are rejected.


### Pagination, Sorting, and Filtering

- Pagination: Use the page query parameter to navigate pages.
_Example:_ GET /wallets/?page=2
- Sorting: Use the ordering query parameter.
_Example:_ GET /wallets/?ordering=balance
- Filtering: Use query parameters to filter results.
_Example:_ GET /wallets/?balance_min=100&balance_max=500

### Swagger Documentation

The API documentation is available at http://localhost:8000/swagger/

### Testing

To run the test suite, execute:

```bash
make test
```

This command will execute the test suite inside a Docker container (if using Docker) or in your local environment.

### Examples of API Requests with cURL

```bash
# 1. Create a Wallet
curl -X POST http://localhost:8000/api/wallets/ \
-H "Content-Type: application/json" \
-d '{
  "label": "My First Wallet",
  "balance": "1000.00"
}'

# 2. Get the List of Wallets (Paginated)
curl -X GET http://localhost:8000/api/wallets/ \
-H "Content-Type: application/json"

# 3. Get a Specific Wallet by ID
curl -X GET http://localhost:8000/api/wallets/1/ \
-H "Content-Type: application/json"

# 4. Update a Wallet
curl -X PUT http://localhost:8000/api/wallets/1/ \
-H "Content-Type: application/json" \
-d '{
  "label": "Updated Wallet Label",
  "balance": "1500.00"
}'

# 5. Partially Update a Wallet (PATCH)
curl -X PATCH http://localhost:8000/api/wallets/1/ \
-H "Content-Type: application/json" \
-d '{
  "balance": "2000.00"
}'

# 6. Delete a Wallet
curl -X DELETE http://localhost:8000/api/wallets/1/

# 7. Create a Transaction (Deposit or Withdrawal)
curl -X POST http://localhost:8000/api/transactions/ \
-H "Content-Type: application/json" \
-d '{
  "txid": "unique_txid_12345",
  "amount": "100.00",
  "wallet": 1
}'

# 8. Get the List of Transactions
curl -X GET http://localhost:8000/api/transactions/ \
-H "Content-Type: application/json"

# 9. Get a Specific Transaction by ID
curl -X GET http://localhost:8000/api/transactions/1/ \
-H "Content-Type: application/json"

# 10. Update a Transaction
curl -X PUT http://localhost:8000/api/transactions/1/ \
-H "Content-Type: application/json" \
-d '{
  "txid": "updated_txid_67890",
  "amount": "200.00",
  "wallet": 1
}'

# 11. Delete a Transaction
curl -X DELETE http://localhost:8000/api/transactions/1/

# 12. Filter Wallets by Balance
curl -X GET "http://localhost:8000/api/wallets/?balance_min=100&balance_max=1000" \
-H "Content-Type: application/json"

# 13. Sort Wallets by Balance
curl -X GET "http://localhost:8000/api/wallets/?ordering=balance" \
-H "Content-Type: application/json"

# 14. Paginate Wallets (Page 2)
curl -X GET "http://localhost:8000/api/wallets/?page=2" \
-H "Content-Type: application/json"
```


## Code Quality
**Linters:** The project uses ruff and black for linting and code formatting.

- To check for linting errors:

```bash
make lint
```

- Automatically fix formatting issues:

```bash
make format
```

**Configuration:** Linter configurations are specified in pyproject.toml.

## Quick Start with Docker

The project includes a docker-compose.yml and Dockerfile for quick setup.


- Start the Application:

```bash
make run
```

- Restart the Application:
    
```bash
make restart
```

- Stop the Application:

```bash
make down
```
## Project Structure

The project structure follows Django best practices:

```
.
├── Makefile
├── README.md
├── infra
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── entrypoint.sh
├── onhires_drf_test_task
│   ├── manage.py
│   ├── onhires_drf_test_task
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── ...
│   └── wallet
│       ├── admin.py
│       ├── apps.py
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       ├── tests.py
│       └── ...
├── poetry.lock
└── pyproject.toml
```


## Additional Notes

- Database Migrations: Migrations are handled by Django’s built-in migration system.
- Indexing: An index is added on the wallet field in the Transaction model to optimize queries.
- Commenting: Code includes comments in unconventional places to explain complex logic.
- Constraints: The project adheres to the specified constraints regarding execution time and memory usage.
- Poetry: Used for dependency management.
- Environment Variables: Configured via a .env.local file.
- Entry Point Script: Ensure execution permission is granted to the entrypoint.sh script:

```bash
chmod +x infra/entrypoint.sh
```

## Admin Interface

Django’s admin interface is available at http://localhost:8000/admin/.

To create a superuser:
```bash
poetry run python onhires_drf_test_task/manage.py createsuperuser
```



## Limitations

- SQLAlchemy: Not used for database migrations; Django’s migration system is utilized instead.

## License

This project is for demonstration purposes and does not have a specific license.
