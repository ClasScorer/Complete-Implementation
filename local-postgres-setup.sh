#!/bin/bash

# Local PostgreSQL Database Setup for Graduation Project
# This script creates a unified PostgreSQL database using podman

set -e

# Database credentials (matching your services)
POSTGRES_USER="user"
POSTGRES_PASSWORD="password"
POSTGRES_DB="graduation_project"

# Container and volume names
CONTAINER_NAME="graduation-project-postgres"
VOLUME_NAME="graduation-project-postgres-data"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Setting up local PostgreSQL database for Graduation Project${NC}"

# Stop and remove existing container if it exists
if podman ps -a --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${YELLOW}⚠️  Stopping and removing existing container: ${CONTAINER_NAME}${NC}"
    podman stop ${CONTAINER_NAME} || true
    podman rm ${CONTAINER_NAME} || true
fi

# Remove existing volume if it exists (optional - comment out to preserve data)
if podman volume ls --format "table {{.Name}}" | grep -q "^${VOLUME_NAME}$"; then
    echo -e "${YELLOW}⚠️  Removing existing volume: ${VOLUME_NAME}${NC}"
    podman volume rm ${VOLUME_NAME} || true
fi

# Create volume for persistent data
echo -e "${GREEN}📦 Creating PostgreSQL data volume...${NC}"
podman volume create ${VOLUME_NAME}

# Run PostgreSQL container
echo -e "${GREEN}🐘 Starting PostgreSQL container...${NC}"
podman run -d \
    --name ${CONTAINER_NAME} \
    -e POSTGRES_USER=${POSTGRES_USER} \
    -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
    -e POSTGRES_DB=${POSTGRES_DB} \
    -p 5432:5432 \
    -v ${VOLUME_NAME}:/var/lib/postgresql/data \
    --restart unless-stopped \
    docker.io/postgres:13

# Wait for PostgreSQL to be ready
echo -e "${GREEN}⏳ Waiting for PostgreSQL to be ready...${NC}"
sleep 10

# Create individual databases for each service
echo -e "${GREEN}🗄️  Creating individual databases...${NC}"

# Function to execute SQL commands
execute_sql() {
    podman exec -i ${CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "$1"
}

# Create databases
echo -e "${YELLOW}Creating database: face_embeddings (Recognition Service)${NC}"
execute_sql "CREATE DATABASE face_embeddings;"

echo -e "${YELLOW}Creating database: student_attention (Attention Service)${NC}"  
execute_sql "CREATE DATABASE student_attention;"

echo -e "${YELLOW}Creating database: attention (Alternative Attention DB)${NC}"
execute_sql "CREATE DATABASE attention;"

echo -e "${YELLOW}Creating database: classcorer (WebApp)${NC}"
execute_sql "CREATE DATABASE classcorer;"

echo -e "${YELLOW}Creating database: hand_raising (Hand-Raising Service)${NC}"
execute_sql "CREATE DATABASE hand_raising;"

# Grant permissions to user for all databases
echo -e "${GREEN}🔑 Granting permissions...${NC}"
execute_sql "GRANT ALL PRIVILEGES ON DATABASE face_embeddings TO ${POSTGRES_USER};"
execute_sql "GRANT ALL PRIVILEGES ON DATABASE student_attention TO ${POSTGRES_USER};"
execute_sql "GRANT ALL PRIVILEGES ON DATABASE attention TO ${POSTGRES_USER};"
execute_sql "GRANT ALL PRIVILEGES ON DATABASE classcorer TO ${POSTGRES_USER};"
execute_sql "GRANT ALL PRIVILEGES ON DATABASE hand_raising TO ${POSTGRES_USER};"

# Show database list
echo -e "${GREEN}📋 Available databases:${NC}"
podman exec -i ${CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "\l"

echo -e "${GREEN}✅ PostgreSQL setup complete!${NC}"
echo ""
echo -e "${GREEN}📝 Connection Information:${NC}"
echo -e "Host: localhost"
echo -e "Port: 5432"
echo -e "Username: ${POSTGRES_USER}"
echo -e "Password: ${POSTGRES_PASSWORD}"
echo ""
echo -e "${GREEN}🔗 Database URLs for your services:${NC}"
echo -e "${YELLOW}Recognition Service:${NC}"
echo -e "  DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/face_embeddings"
echo ""
echo -e "${YELLOW}Attention Service:${NC}"
echo -e "  DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/student_attention"
echo -e "  # OR DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/attention"
echo ""
echo -e "${YELLOW}Hand-Raising Service:${NC}"
echo -e "  DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/hand_raising"
echo ""
echo -e "${YELLOW}ClassScorer WebApp:${NC}"
echo -e "  DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/classcorer"
echo ""
echo -e "${GREEN}🛠️  Management Commands:${NC}"
echo -e "Start container:  podman start ${CONTAINER_NAME}"
echo -e "Stop container:   podman stop ${CONTAINER_NAME}"
echo -e "View logs:        podman logs ${CONTAINER_NAME}"
echo -e "Connect to DB:    podman exec -it ${CONTAINER_NAME} psql -U ${POSTGRES_USER} -d classcorer"
echo ""
echo -e "${GREEN}🗑️  To completely remove (including data):${NC}"
echo -e "podman stop ${CONTAINER_NAME} && podman rm ${CONTAINER_NAME} && podman volume rm ${VOLUME_NAME}" 