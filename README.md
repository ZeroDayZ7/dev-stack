# dev-stack

A shared, lightweight local AI infrastructure stack providing offline AI services for development environments.

This stack contains reusable AI microservices that can be shared across multiple projects:

- **Ollama** - local Large Language Model (LLM) runtime
- **Piper TTS** - offline Text-to-Speech service
- **Whisper STT** - offline Speech-to-Text service

The goal of `dev-stack` is to run AI services once and allow multiple applications (for example Hanasu, Obywatel App, ERP systems) to connect to the same infrastructure without duplicating containers and AI models.

---

## Architecture

```
                 dev-stack-network
                       |
        --------------------------------
        |              |               |
     Ollama          Piper          Whisper
     :11434          :8000           :8001
        |
        |
   Other applications

   Hanasu
   Obywatel App
   ERP
```

All services communicate through a shared Docker network.

---

# Prerequisites

Required:

- Docker
- Docker Compose

Create the shared Docker network once:

```bash
docker network create dev-stack-network
```

This network is external and can be used by multiple Docker Compose projects.

---

# Directory Structure

Example:

```
dev-stack/
│
├── docker-compose.yml
├── .env
│
├── piper/
│   └── Dockerfile
│
├── whisper/
│   └── Dockerfile
│
└── README.md
```

---

# Quick Start

## 1. Configure environment

Copy the example environment file:

```bash
cp .env.example .env
```

Adjust values if needed.

---

## 2. Start AI infrastructure

Build and start all services:

```bash
docker compose up -d --build
```

Check running containers:

```bash
docker ps
```

---

# Available Services

| Service     | Address                  | Description                |
| ----------- | ------------------------ | -------------------------- |
| Ollama      | `http://localhost:11434` | Local LLM API              |
| Piper TTS   | `http://localhost:8000`  | Offline voice generation   |
| Whisper STT | `http://localhost:8001`  | Offline speech recognition |

---

One AI stack, many applications.
