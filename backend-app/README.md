# FastAPI Backend with PostgreSQL

A REST API built with FastAPI for tracking financial records (income and expenses) with PostgreSQL database.

## Features

- ✅ RESTful API with FastAPI
- ✅ PostgreSQL database integration with SQLAlchemy ORM
- ✅ Financial record tracking (income/expense)
- ✅ Category classification (food, car, rent)
- ✅ Precise currency handling with Decimal type
- ✅ Photo attachments with Azure Blob Storage
- ✅ File upload validation (size, type)
- ✅ Filtering by category and record type
- ✅ CRUD operations with validation
- ✅ Request/response validation with Pydantic
- ✅ Automatic API documentation (Swagger UI & ReDoc)
- ✅ Docker containerization
- ✅ Docker Compose for local development
- ✅ Health check endpoints
- ✅ CORS middleware
- ✅ Connection pooling

## Project Structure

```
backend-app/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # Database connection and session management
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic models for validation
│   ├── crud.py              # CRUD operations
│   └── routers/
│       ├── __init__.py
│       └── items.py         # API endpoints for items
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── Dockerfile              # Container image definition
├── docker-compose.yml      # Local development setup
└── README.md               # This file
```

## Prerequisites

- Python 3.11+
- PostgreSQL 16+ (or use Docker Compose)
- Docker and Docker Compose (optional, for containerized setup)

## Quick Start with Docker Compose

The easiest way to run the application locally is using Docker Compose:

```bash
# Navigate to the project directory
cd backend-app

# Start the application and PostgreSQL database
docker-compose up -d

# Check logs
docker-compose logs -f api

# Stop the application
docker-compose down

# Stop and remove volumes (removes database data)
docker-compose down -v
```

The API will be available at:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Local Development Setup

### 1. Set up PostgreSQL

Install PostgreSQL locally or use Docker:

```bash
docker run -d \
  --name postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=fastapi_db \
  -p 5432:5432 \
  postgres:16-alpine
```

### 2. Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
.\venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration (optional)
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fastapi_db
# API_HOST=0.0.0.0
# API_PORT=8000
```

### 4. Run the Application

```bash
# From the backend-app directory
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health Check

- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint

### Financial Records

- `POST /items/` - Create a new financial record
- `GET /items/` - List all records (with pagination and filtering)
- `GET /items/{item_id}` - Get a specific record by ID
- `PUT /items/{item_id}` - Update a financial record
- `DELETE /items/{item_id}` - Delete a financial record

**Query Parameters for GET /items/:**
- `skip` - Number of items to skip (pagination)
- `limit` - Maximum number of items to return
- `category` - Filter by category (food, car, rent)
- `record_type` - Filter by type (income, expense)

## API Usage Examples

### Create an Expense Record

```bash
curl -X POST "http://localhost:8000/items/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Grocery Shopping",
    "description": "Weekly groceries",
    "category": "food",
    "record_type": "expense",
    "sum": "150.75"
  }'
```

### Create an Income Record

```bash
curl -X POST "http://localhost:8000/items/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Monthly Salary",
    "description": "December salary",
    "record_type": "income",
    "sum": "5000.00"
  }'
```

### Get All Records

```bash
curl "http://localhost:8000/items/"
```

### Get Records with Pagination

```bash
curl "http://localhost:8000/items/?skip=0&limit=10"
```

### Filter by Category

```bash
# Get all food expenses
curl "http://localhost:8000/items/?category=food"

# Get all car-related records
curl "http://localhost:8000/items/?category=car"
```

### Filter by Record Type

```bash
# Get all income records
curl "http://localhost:8000/items/?record_type=income"

# Get all expenses
curl "http://localhost:8000/items/?record_type=expense"
```

### Combined Filters

```bash
# Get food expenses only
curl "http://localhost:8000/items/?category=food&record_type=expense"

# Get rent expenses with pagination
curl "http://localhost:8000/items/?category=rent&record_type=expense&skip=0&limit=5"
```

### Get a Specific Record

```bash
curl "http://localhost:8000/items/1"
```

### Update a Record

```bash
curl -X PUT "http://localhost:8000/items/1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Grocery Shopping",
    "sum": "175.50"
  }'
```

### Delete a Record

```bash
curl -X DELETE "http://localhost:8000/items/1"
```

## Database Schema

### Items Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| name | VARCHAR(255) | Record name (required) |
| description | TEXT | Record description (optional) |
| category | ENUM | Category: food, car, rent (optional, indexed) |
| record_type | ENUM | Type: income or expense (required, indexed) |
| sum | NUMERIC(10,2) | Amount in currency (required, must be > 0) |
| photo_url | VARCHAR(500) | Azure Blob Storage URL for photo (optional) |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

### Enumerations

**CategoryEnum:**
- `food` - Food and groceries
- `car` - Car-related expenses
- `rent` - Rent and housing

**RecordTypeEnum:**
- `income` - Income records
- `expense` - Expense records

## Testing

You can test the API using:

1. **Swagger UI**: Navigate to http://localhost:8000/docs
2. **ReDoc**: Navigate to http://localhost:8000/redoc
3. **curl**: Use the examples above
4. **Postman/Insomnia**: Import the OpenAPI schema from `/openapi.json`

## Building and Running with Docker

### Build the Docker Image

```bash
docker build -t fastapi-backend:latest .
```

### Run the Container

```bash
# Run with environment variables
docker run -d \
  --name fastapi-app \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5432/fastapi_db \
  fastapi-backend:latest
```

## Deployment Considerations

For production deployment:

1. **Environment Variables**: Use proper secrets management
2. **CORS**: Configure `allow_origins` in `main.py` with specific domains
3. **Database**: Use managed PostgreSQL service (e.g., AWS RDS, Azure Database)
4. **Security**: Add authentication and authorization
5. **Logging**: Configure proper logging and monitoring
6. **Rate Limiting**: Implement rate limiting for API endpoints
7. **Database Migrations**: Use Alembic for schema migrations

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | postgresql://postgres:postgres@localhost:5432/fastapi_db |
| API_HOST | API host address | 0.0.0.0 |
| API_PORT | API port number | 8000 |

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check PostgreSQL logs
docker logs postgres

# Test connection
psql -h localhost -U postgres -d fastapi_db
```

### Application Logs

```bash
# View Docker Compose logs
docker-compose logs -f api

# View container logs
docker logs fastapi-app
```

## License

This project is part of the kubernetes-lessons repository.

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
