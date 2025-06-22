# 🎉 PostgreSQL Database Setup Complete!

Your local PostgreSQL database has been successfully set up using podman with all the required databases for your graduation project microservices.

## 📊 Database Information

**Container Status:** ✅ Running  
**Container Name:** `graduation-project-postgres`  
**Host:** localhost  
**Port:** 5432  
**Username:** user  
**Password:** password  

## 🗄️ Available Databases

| Database Name | Service | Purpose |
|--------------|---------|---------|
| `face_embeddings` | Recognition Service | Stores face recognition embeddings |
| `student_attention` | Attention Service | Stores attention tracking data |
| `attention` | Attention Service (Alternative) | Alternative attention database |
| `classcorer` | ClassScorer WebApp | Main application database |
| `hand_raising` | Hand-Raising Service | Hand-raising detection data |
| `graduation_project` | Main | Master database |

## 🔗 Database URLs for Each Service

### Recognition Service
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/face_embeddings
```

### Attention Service
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/student_attention
```

### Hand-Raising Service
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/hand_raising
```

### ClassScorer WebApp
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/classcorer
```

## ⚙️ Environment Configuration

To use the local database with your services, you can:

1. **Copy the provided environment examples:**
   ```bash
   # For Recognition Service
   cp Recognition/env-local-example Recognition/.env
   
   # For Attention Service
   cp Attention/env-local-example Attention/.env
   
   # For Hand-Raising Service
   cp Hand-Raising/env-local-example Hand-Raising/.env
   
   # For ClassScorer WebApp
   cp classcorer-webapp/env-local-example classcorer-webapp/.env.local
   ```

2. **Or manually create .env files** with the database URLs above.

## 🛠️ Management Commands

### Container Management
```bash
# Start container
podman start graduation-project-postgres

# Stop container
podman stop graduation-project-postgres

# View container logs
podman logs graduation-project-postgres

# Restart container
podman restart graduation-project-postgres
```

### Database Access
```bash
# Connect to main database
podman exec -it graduation-project-postgres psql -U user -d graduation_project

# Connect to classcorer database
podman exec -it graduation-project-postgres psql -U user -d classcorer

# Connect to face_embeddings database
podman exec -it graduation-project-postgres psql -U user -d face_embeddings

# List all databases
podman exec -i graduation-project-postgres psql -U user -d graduation_project -c "\l"
```

### Database Operations
```bash
# Backup a database
podman exec graduation-project-postgres pg_dump -U user classcorer > classcorer_backup.sql

# Restore a database
podman exec -i graduation-project-postgres psql -U user -d classcorer < classcorer_backup.sql
```

## 🧹 Cleanup (if needed)

To completely remove the database setup:

```bash
# Stop and remove container
podman stop graduation-project-postgres
podman rm graduation-project-postgres

# Remove persistent data volume
podman volume rm graduation-project-postgres-data
```

## 🚀 Next Steps

1. **Set up environment files** for each service using the examples provided
2. **Run database migrations** for each service:
   ```bash
   # In each service directory with Prisma
   vf activate Grad  # Make sure your virtual environment is active
   prisma migrate deploy
   ```
3. **Start your services** and they should connect to the local database

## 🔧 Troubleshooting

- **Connection refused:** Make sure the container is running with `podman ps -a`
- **Permission denied:** Check that the user/password combination is correct
- **Database not found:** Verify the database name matches the service configuration
- **Port conflict:** Make sure port 5432 is not used by another PostgreSQL instance

Your local PostgreSQL database is now ready for development! 🎯 