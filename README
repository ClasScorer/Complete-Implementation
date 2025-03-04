# ClasScorer Complete System

## Overview

This repository contains the complete system for the ClasScorer project, including all components:

- Attention
- Hand-Raising
- Recognition
- Localization
- Frontend

You can run each component separately or together.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/ClasScorer/ClasScorer.git
cd ClasScorer
```

2. Install dependencies for each component:

```bash
cd Attention
pip install -r requirements.txt

cd Hand-Raising
pip install -r requirements.txt

cd Recognition
pip install -r requirements.txt


cd Localization
pip install -r requirements.txt

cd Frontend
pip install -r requirements.txt
```

3. Run each component:

```bash
cd Attention
docker build -t attention .
docker run -d -p 8000:8000 attention

cd Hand-Raising
docker build -t hand-raising .
docker run -d -p 8001:8001 hand-raising

cd Recognition
docker build -t recognition .
docker run -d -p 8002:8002 recognition


cd Localization
docker build -t localization .
docker run -d -p 8003:8003 localization

cd Frontend
docker build -t frontend .
docker run -d -p 8004:8004 frontend
```

### Running the system as a whole

```bash
docker-compose up
```

#### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

