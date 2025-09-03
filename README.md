# authGhost API

authGhost is Phoenone's centralized authentication and access management API, designed for developers building multi-service applications. Built with FastAPI, SQLAlchemy, and MySQL.

## Features

- 🔐 **Multi-tenant Authentication**: Support for multiple organizations
- 🏢 **Organization Management**: Multi-tenant organization structure
- 👥 **Role-Based Access Control (RBAC)**: Service-specific roles with JSON permissions
- 🔑 **JWT Authentication**: Secure token-based authentication with service-specific access
- 📊 **Subscription Management**: Organization-level subscription tiers and feature access
- 🚀 **FastAPI**: Modern, fast web framework with automatic API documentation
- 🗄️ **MySQL Database**: Robust relational database backend
- 🐳 **Docker Support**: Containerized deployment ready

## Description

authGhost provides a secure and consistent way to handle:

- **User authentication and service-specific JWT token issuance**
- **Role-based access control (RBAC) across multiple services**
- **Organization-level subscription management and feature access**
- **Multi-tenant support for SaaS platforms**
- **Token refresh and optional revocation for secure session management**

Developers can integrate authGhost with Laravel, Symfony, SpringBoot, ExpressJS, or any other microservices, ensuring that authentication, authorization, and subscription checks are consistent across all products. It is optimized for stateless JWT validation but also supports token introspection for revocable access.

## Tech Stack

- **Backend**: FastAPI 0.104.1
- **Database**: MySQL 8.0 with SQLAlchemy 2.0
- **Authentication**: JWT with bcrypt password hashing
- **Validation**: Pydantic 2.5.0
- **Logging**: Structlog with JSON formatting
- **Containerization**: Docker & Docker Compose

## Quick Start

### Prerequisites

- Python 3.11+
- MySQL 8.0+ (running locally)
- Redis (optional, for session management)

**Note for macOS users**: If you encounter issues installing `mysqlclient`, the project now uses `pymysql` which is more compatible with macOS. No additional system dependencies are required.

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd authService
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: source venv/Scripts/activate
   ```

3. **Set up local MySQL database**
   ```bash
   # Ensure MySQL is running locally
   python scripts/setup_local_mysql.py
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   ```bash
   cp env.example .env
   # The setup script will update this automatically
   ```

6. **Initialize database**
   ```bash
   python scripts/setup.py
   ```

7. **Start the application**
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

8. **Access the API**
   - Swagger UI: http://127.0.0.1:8000/docs
   - ReDoc: http://127.0.0.1:8000/redoc
   - Health Check: http://127.0.0.1:8000/api/v1/health

### Docker Deployment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/refresh` - Refresh access token

### Multi-tenant Management
- `GET/POST/PUT/DELETE /api/v1/schools` - School management
- `GET/POST/PUT/DELETE /api/v1/campuses` - Campus management
- `GET/POST/PUT/DELETE /api/v1/roles` - Role management
- `GET/POST/PUT/DELETE /api/v1/users` - User management

## Environment Variables

Key environment variables (see `.env.example` for complete list):

```env
# Database
DATABASE_URL=mysql://user:password@localhost:3306/auth_db

# Security
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server
HOST=127.0.0.1
PORT=8000
DEBUG=true
```

## Database Schema

The service uses a multi-tenant architecture with the following key entities:

- **Schools**: Top-level organizations (tenants)
- **Campuses**: Physical locations within schools
- **Users**: User accounts with role-based access
- **Roles**: Permission groups for users
- **Permissions**: Granular access controls

## Development

### Code Quality

The project uses several tools for code quality:

- **Formatting**: isort, black
- **Linting**: flake8, ruff
- **Type Checking**: mypy
- **Security**: bandit

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## License

[Add your license here]

## Contributing

[Add contribution guidelines here] 