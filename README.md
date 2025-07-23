# Research Assistant
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/) [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/) [![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/) [![Docker Compose](https://img.shields.io/badge/Docker_Compose-2496ED?style=flat&logo=docker&logoColor=white)](https://docs.docker.com/compose/)

## Table of Contents

- [Research Assistant](#top)
  - [Table of Contents](#Table-of-Contents)
  - [Overview](#Overview)
  - [Features](#Features)
  - [Technologies Used](#Technologies-Used)
  - [Getting Started](#Getting-Started)
    - [Prerequisites](#Prerequisites)
    - [Installation](#Installation)
      - [1\. Clone the Repository](#1-Clone-the-Repository)
      - [2\. Configure Environment Variables](#2-Configure-Environment-Variables)
      - [3\. Build and Run with Docker Compose](#3-Build-and-Run-with-Docker-Compose)
  - [Development](#Development)
    - [Backend Development](#Backend-Development)
    - [Frontend Development](#Frontend-Development)
  - [License](#License)

## Overview

The Research Assistant is an AI-powered application designed to streamline the research process. It provides an intuitive chat interface where users can interact with an intelligent agent to conduct research, retrieve information, and manage their research sessions efficiently. The application is built with a modern tech stack, featuring a FastAPI backend, a SvelteKit frontend, and orchestrated using Docker Compose for easy deployment and scalability.

## Features

- **AI-Powered Research:** Interact with an intelligent agent to assist with research queries.
- **Interactive Chat Interface:** A responsive and user-friendly chat experience for seamless interaction.
- **Research Session Management:** Create, manage, and review different research sessions.
- **Modular Architecture:** Separated backend and frontend services for maintainability and scalability.
- **Dockerized Deployment:** Easy setup and deployment using Docker and Docker Compose.

## Technologies Used

- **Backend:**
  - [FastAPI](https://fastapi.tiangolo.com/) - High-performance web framework.
  - [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit and Object-Relational Mapper (ORM).
  - [PostgreSQL](https://www.postgresql.org/) - Robust relational database.
  - [Langchain](https://www.langchain.com/) - Framework for developing applications powered by language models.
- **Frontend:**
  - [SvelteKit](https://kit.svelte.dev/) - Web framework for building highly performant Svelte apps.
  - [TypeScript](https://www.typescriptlang.org/) - Superset of JavaScript that adds static types.
  - [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework for rapid UI development.
- **Deployment & Orchestration:**
  - [Docker](https://www.docker.com/) - Containerization platform.
  - [Docker Compose](https://docs.docker.com/compose/) - Tool for defining and running multi-container Docker applications.
  - [Nginx](https://www.nginx.com/) - High-performance HTTP server and reverse proxy.

## Getting Started

Follow these instructions to set up and run the Research Assistant on your local machine.

### Prerequisites

Before you begin, ensure you have the following installed:

- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [Docker](https://github.com/docker/docker-install.git) (includes Docker Engine and Docker Compose)

### Installation

#### 1\. Clone the Repository

First, clone the project repository to your local machine:

```bash
git clone https://github.com/mh-saeidi/research-assistant.git
```

```bash
cd research-assistant
```

#### 2\. Configure Environment Variables

The project uses environment variables for sensitive information and configuration.

Navigate to the backend directory and create a .env file based on the provided example:

```bash
cd backend
```

```bash
cp .env.example .env
```

Now, open backend/.env in your text editor and fill in the required values.

Make sure to create the .env file in the root directory to configure Docker Compose environment variables!

#### 3\. Build and Run with Docker Compose

From the root directory of the project (where docker-compose.yml is located), run the following command to build the Docker images and start all services:

```bash
docker compose up --build -d
```

This command will:

- Build the backend Docker image.
- Build the frontend Docker image.
- Set up a PostgreSQL database container.
- Configure an Nginx reverse proxy to route requests.

Once all services are up and running, you can access the application from the ip address or localhost

## Development

If you wish to develop on the project, you can run the backend and frontend services independently.

### Backend Development

1. **Install dependencies:**

```bash
cd backend
```

```bash
pip install -r requirements.txt
```

1. **Run database locally (optional, or use Docker Compose DB):**

Ensure your DATABASE_URL in backend/.env points to a local PostgreSQL instance if not using the Docker Compose db service.

1. **Run the FastAPI application:**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend will be accessible at <http://localhost:8000>.

### Frontend Development

1. **Install dependencies:**

```bash
cd frontend
```

```bash
npm install
```

1. **Run the SvelteKit development server:**

```bash
npm run dev
```

The frontend will be accessible at <http://localhost:3000>. You may need to adjust the API endpoint in the frontend code to point to your local backend (e.g., <http://localhost:8000>) if not using Nginx.

## License

See the [LICENSE](https://github.com/mh-saeidi/research-assistant/blob/main/LICENSE) file for more details.
