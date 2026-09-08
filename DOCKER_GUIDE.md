# HUB - Digital Public Administration Project

## Docker Setup and Running Guide

### Prerequisites
- Docker and Docker Compose installed
- Adequate disk space for MySQL and Redis volumes

### Project Structure
```
HUB/                     # Backend service
├── backend/            # FastAPI application
├── database/           # Database configuration
├── plugin/             # Plugins (Scanner, WebView)
├── OCR/               # OCR module
└── Dockerfile         # Backend Docker image

HUB_fe/                 # HUB Frontend (React/Vite)
└── HUB_fe/
    └── Dockerfile

user_UI/                # User UI Frontend (React/Vite)
└── user_UI/
    └── Dockerfile
```

### Services Overview
- **MySQL (3308)**: Database server
- **Redis (6380)**: Cache and message queue
- **Backend (8000)**: FastAPI server
- **HUB Frontend (5173)**: Admin/Staff UI
- **User UI (5174)**: End-user UI

### Setup Instructions

#### 1. Navigate to the project root
```bash
cd HUB
```

#### 2. Environment Configuration
Create or update the following `.env` files:

**`backend/.env`** (for local development):
```
SCANNER_SAVE_PATH=D:\scanned_files
SETTING_PATH=./settings.xml
REDIS_HOST=localhost
REDIS_PASSWORD=redispassword
REDIS_PORT=6380
```

**`database/.env.database`** (for local development):
```
DB_HOST=localhost
DB_PORT=3308
DB_USER=hub_user
DB_PASSWORD=2e95b4d498fab9ed41cfc3a3d6ec58e9069b31b71057391a1a6ca2cef739faa3
DB_DATABASE=HUB_db
DB_POOL_SIZE=10
```

#### 3. Build and Run with Docker Compose

**Build all images:**
```bash
docker-compose build
```

**Start all services:**
```bash
docker-compose up -d
```

**View logs:**
```bash
docker-compose logs -f
```

**Stop all services:**
```bash
docker-compose down
```

**Remove volumes (WARNING: deletes data):**
```bash
docker-compose down -v
```

### Accessing the Application

After services are running:

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **HUB Frontend**: http://localhost:5173
- **User UI**: http://localhost:5174
- **Database**: localhost:3308
  - User: `hub_user`
  - Password: `2e95b4d498fab9ed41cfc3a3d6ec58e9069b31b71057391a1a6ca2cef739faa3`
- **Redis**: localhost:6380
  - Password: `redispassword`

### Service Dependencies

Services are configured with health checks and dependency management:

1. MySQL and Redis start first
2. Backend waits for MySQL and Redis to be healthy
3. Frontend services depend on Backend

### Troubleshooting

**Backend fails to connect to database:**
- Check if MySQL is running: `docker logs HUB-mysql-db`
- Verify database credentials in `.env` files
- Ensure port 3308 is not in use

**Backend fails to connect to Redis:**
- Check if Redis is running: `docker logs HUB-redis-db`
- Verify Redis password: `redispassword`
- Ensure port 6380 is not in use

**Frontend can't reach backend:**
- Verify backend is running: `docker logs HUB-backend`
- Check network connectivity between services
- Ensure `VITE_API_URL` is correct in frontend services

**Volume mounting issues:**
- Ensure `D:\scanned_files` directory exists (Windows)
- On Linux/Mac, adjust paths in docker-compose.yml
- Check file permissions for mounted volumes

### Building Specific Services

**Build only backend:**
```bash
docker-compose build backend
```

**Build only frontend:**
```bash
docker-compose build hub-fe user-ui
```

### Development Notes

- Database initialization runs from `database/database.sql`
- Static files (scanned documents) are mounted as volumes
- Settings are persisted in `settings.xml`
- All services use a shared Docker network: `hub-network`

### Performance Tuning

**Increase database connection pool:**
Update `DB_POOL_SIZE` in `.env.database` (default: 10)

**Adjust Redis memory:**
Modify Redis command in docker-compose.yml

### Security Notes

⚠️ **DO NOT use default credentials in production!**
- Change MySQL password
- Change Redis password
- Use strong credentials
- Store secrets in secure vaults
