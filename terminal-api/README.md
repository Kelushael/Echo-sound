# Terminal API

This module provides a small HTTP service for executing terminal commands. It is intended for controlled environments where remote command execution is required.

## Features
- REST API defined in `terminal_api.yaml`.
- Flask-based backend (`app.py`).
- Containerized with `Dockerfile`.
- Terraform scripts for AWS Fargate deployment.
- Load testing with Locust (`locustfile.py`).
- Example GPT prompts for integrating with language models.

## Quick Start
1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Run the server:
   ```sh
   API_KEY=mykey python app.py
   ```
3. Execute a command:
   ```sh
   curl -X POST http://localhost:3000/execute \
     -H "X-API-Key: mykey" \
     -H "Content-Type: application/json" \
     -d '{"command": "ls"}'
   ```

## Deployment
See `terraform/` for AWS deployment via ECS and `Dockerfile` for containerization instructions.
