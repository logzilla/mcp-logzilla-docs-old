<!-- @@@title:Installation of LogZilla AI Copilot Module@@@ -->

# Installation of LogZilla AI Copilot Module

The LogZilla Copilot module requires manual installation as it is not included
in the standard LogZilla installation package. This module must be installed on
the same host where LogZilla is running to ensure proper connectivity to the
same Docker network.

## Prerequisites

- Docker and Docker Compose installed
- LogZilla instance running on the same host (minimum version v6.36)
- Access to a suitable LLM (such as OpenAI, Anthropic, or a local LLM hosted
  with Ollama server)

## Installation Steps

### 1. Prepare the Directory Structure

Create a dedicated directory for the LogZilla AI Copilot installation:

```bash
mkdir lz-ai
cd lz-ai
```

### 2. Pull Current LogZilla AI Image

```bash
docker pull logzilla/ai
```

### 3. Create Configuration Files

The installation requires two configuration files in the directory:

#### Create compose.yaml

Create a file named `compose.yaml` with the following content:

```yaml
services:
    postgres:
        image: postgres:13.3
        environment: &env_postgres
            POSTGRES_USER: ${POSTGRES_USER:-postgres}
            POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
            POSTGRES_DB: ${POSTGRES_DB:-ai}
        volumes:
            - postgres:/var/lib/postgresql/data
        restart: always
    qdrant:
        image: "qdrant/qdrant"
        ports:
            - 6333:6333
        volumes:
            - qdrant:/qdrant/storage
        restart: always
    dcm_installer:
        image: logzilla/ai
        environment:
            <<: *env_postgres
        links:
            - qdrant
            - postgres
        depends_on:
            - qdrant
            - postgres
        volumes:
            - ./config.yaml:/app/config.yaml
        command: ["/app/bin/dcm", "install", "-i", "/app/dcm-install"]
    web:
        image: logzilla/ai
        environment:
            APP_NAME: "web"
            <<: *env_postgres
        links:
            - qdrant
            - postgres
        depends_on:
            dcm_installer:
                condition: service_completed_successfully
        volumes:
            - ./config.yaml:/app/config.yaml
        restart: unless-stopped
        command: ["/app/bin/web-bot.py", "--port", "80"]
        networks:
            default:
            lz_main:
                aliases:
                    - ai-web
volumes:
    qdrant: ~
    postgres: ~
networks:
  lz_main:
    external: true
```

#### Create config.yaml

Create a file named `config.yaml` with the following content:

```yaml
# Configuration file for LogZilla AI bot

# URL to the bot's web interface, used when creating shared links
# IMPORTANT: Replace with your LogZilla URL (where you access LogZilla)
base_url: "http://your-logzilla-server/ai/"

# This section defines LLM models that can be used
# The first model is selected as default for new users
# Configure the API keys below for the models you want to use
llms:
  # Anthropic Claude models
  - name: claude-sonnet
    type: anthropic
    api_key: &CLAUDE_API_KEY "sk-a..."
    api_model_name: claude-3-5-sonnet-latest
    context_window: 200000
  - name: claude-haiku
    type: anthropic
    api_key: *CLAUDE_API_KEY
    api_model_name: claude-3-5-haiku-latest
    context_window: 200000
  
  # OpenAI models
  - name: gpt-4o
    type: openai
    api_key: &OPENAI_API_KEY "sk-..."
    context_window: 128000
  - name: gpt-4o-mini
    type: openai
    api_key: *OPENAI_API_KEY
    context_window: 128000
  - name: gpt-o3
    type: openai
    api_key: *OPENAI_API_KEY
    api_model_name: o3-mini
    context_window: 200000
  
  # For local Ollama models
  - name: local-llama
    type: ollama
    api_model_name: llama3
    base_url: "http://your-ollama-server:11434"
    context_window: 128000

# =========================================================
# You probably shouldn't change anything below this line
# =========================================================

# Directories with cached data (for speeding up startup)
models:
  hf_home: /models/cache/hf
  sentence_transformers_home: /models/cache/sentence_transformers
  embeddings: "/models/cache/all-mpnet-base-v2"

# vector database for documents collections
qdrant:
  endpoint: "http://qdrant:6333"
```

**Important Configuration Notes:**

1. Set the `base_url` parameter to match your LogZilla server URL
   (example: `http://logzilla.company.com/ai/`)

2. Configure the LLM models:
   - For cloud-based models (OpenAI, Anthropic), replace the placeholder API
     keys with valid keys
   - For local Ollama models, update the `base_url` with your Ollama server
     address

Multiple models can be configured as needed. The first model in the list
serves as the default selection for users.

### 4. Start the Services

Launch the LogZilla AI services using Docker Compose:

```bash
docker compose up -d
```

This command initiates the following services:

- PostgreSQL database (for storing conversation history)
- Qdrant vector database (for embeddings and semantic search)
- Docs Collection installer (installs available documentation collections,
  which may require additional time during the initial startup)
- Web interface for the AI assistant

It also connects the services to the `lz_main` Docker network, which is
automatically created by LogZilla.

### 5. Enable the AI Module in LogZilla

Users should log in to their LogZilla instance and navigate to the `Settings`
page. Under the "System Settings" tab, in the "Front" section, locate
"AI Enabled" and set it to "On". This will restart the LogZilla UI. After a
few seconds, the "Copilot" link should redirect to the Copilot UI page.

### 6. Test the Integration

Access the AI chat interface by navigating to the LogZilla URL with the `/ai`
path appended:

```text
{LogZilla-URL}/ai
```

## Troubleshooting

- If redirection to the documentation page occurs after enabling the feature
  when accessing the /ai URL, check the LogZilla logs at
  `/var/log/logzilla/logzilla.log` for errors
- For unresponsive AI services, examine the Docker logs using the command
  `docker compose logs`
- Verify that the LogZilla network (`lz_main`) exists in the Docker
  environment
- Confirm that all API keys in the `config.yaml` file are valid and current

## Upgrading

To upgrade the LogZilla Copilot module, follow these steps in the installation
 directory:

1. Pull all updated images:

   ```bash
   docker compose pull
   ```

2. Recreate all containers with the new images:

   ```bash
   docker compose up -d
   ```

3. Verify the upgrade was successful:

   ```bash
   docker compose ps
   ```

This ensures all services are updated consistently while preserving any custom
configurations.

For additional information, consult the
[LogZilla documentation](https://docs.logzilla.net) or contact LogZilla
support.
