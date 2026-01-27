# Flask Frontend for Financial Tracker

A simple web interface built with Flask for managing financial records (income and expenses) via the FastAPI backend.

## Features

- ✅ Clean and responsive web interface
- ✅ Create new financial records
- ✅ Photo attachment upload
- ✅ View all records with summary cards
- ✅ Filter by category (food, car, rent)
- ✅ Filter by record type (income, expense)
- ✅ Calculate totals and balance
- ✅ View full-size photos in new tab
- ✅ Client-side photo preview
- ✅ File validation (size, format)
- ✅ User-friendly error handling
- ✅ Form validation
- ✅ Docker containerization

## Project Structure

```
frontend-app/
├── app.py                  # Flask application
├── templates/
│   ├── base.html          # Base template with navigation
│   ├── index.html         # Records list page
│   └── create.html        # Create record form
├── static/
│   └── style.css          # Styles
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── Dockerfile            # Container image definition
└── README.md             # This file
```

## Prerequisites

- Python 3.11+
- Backend API running (see [../backend-app](../backend-app/README.md))
- Docker and Docker Compose (optional)

## Quick Start with Docker Compose

The easiest way to run both frontend and backend together:

```bash
# Navigate to the backend-app directory
cd backend-app

# Start all services (PostgreSQL, FastAPI backend, Flask frontend)
docker-compose up -d

# Check logs
docker-compose logs -f frontend

# Stop all services
docker-compose down
```

The frontend will be available at:
- **Frontend**: http://localhost:8001
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Local Development Setup

### 1. Ensure Backend is Running

Make sure the FastAPI backend is running at http://localhost:8000 (see [../backend-app](../backend-app/README.md))

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

# Edit .env if needed (default values should work for local development)
# BACKEND_URL=http://localhost:8000
# FLASK_HOST=0.0.0.0
# FLASK_PORT=5000
```

### 4. Run the Application

```bash
# From the frontend-app directory
python app.py
```

Visit http://localhost:8001 in your browser.

## Application Features

### Home Page (Records List)

- View all financial records in a table
- Summary cards showing:
  - Total income
  - Total expenses
  - Current balance
- Filter records by:
  - Category (food, car, rent)
  - Record type (income, expense)
- Clear filters option

### Create Record Page

- Form to create new records with fields:
  - **Name** (required): Record name/description
  - **Description** (optional): Additional details
  - **Record Type** (required): Income or Expense
  - **Category** (optional): Food, Car, or Rent
  - **Amount** (required): Positive decimal value

### Error Handling

The application handles various error scenarios gracefully:

- **Backend API unavailable**: Shows user-friendly message
- **Connection timeout**: Informs user to try again
- **Validation errors**: Displays specific field errors
- **Form validation**: Client-side and server-side validation

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| BACKEND_URL | FastAPI backend URL | http://localhost:8000 |
| SECRET_KEY | Flask secret key for sessions | dev-secret-key-change-in-production |
| FLASK_HOST | Flask host address | 0.0.0.0 |
| FLASK_PORT | Flask port number | 8001 |
| FLASK_DEBUG | Enable debug mode | False |

## API Integration

The frontend communicates with the following backend endpoints:

- `GET /items/` - List records with optional filters
- `POST /items/` - Create new record

All API requests include:
- 5-second timeout
- Comprehensive error handling
- User-friendly error messages

## Building Docker Image

```bash
# Build the image
docker build -t flask-frontend:latest .

# Run the container
docker run -d \
  --name flask-frontend \
  -p 8001:8001 \
  -e BACKEND_URL=http://host.docker.internal:8000 \
  flask-frontend:latest
```

## Development Tips

1. **Hot Reload**: When running with Docker Compose, the frontend supports hot reload. Changes to Python files will automatically restart the server.

2. **Debugging**: Set `FLASK_DEBUG=true` in your `.env` file for detailed error pages.

3. **Testing Backend Connection**: Visit `/health` endpoint to check if the frontend is running.

4. **Customization**: Edit `static/style.css` to customize the appearance.

## Project Dependencies

- **Flask**: Web framework
- **requests**: HTTP library for API calls
- **python-dotenv**: Environment variables management

## Troubleshooting

### Frontend Can't Connect to Backend

```bash
# Check if backend is running
curl http://localhost:8000/health

# Check backend logs
docker logs fastapi-app

# Verify BACKEND_URL environment variable
echo $BACKEND_URL
```

### Port Already in Use

```bash
# Change FLASK_PORT in .env file
FLASK_PORT=8002

# Or when using docker-compose, change the port mapping:
# ports:
#   - "8002:8001"
```

### Application Not Updating

```bash
# Restart the Flask development server
# Or rebuild Docker container:
docker-compose up -d --build frontend
```

## Screenshots

### Home Page
- Summary cards with income, expenses, and balance
- Filterable table of all records
- Clear and responsive design

### Create Record Form
- Easy-to-use form with validation
- Helpful tips and descriptions
- Real-time error feedback

## License

This project is part of the kubernetes-lessons repository.

## Related Documentation

- [Backend API Documentation](../backend-app/README.md)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Jinja2 Templates](https://jinja.palletsprojects.com/)
