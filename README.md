# Datura-ai-FastAPI-Task

> This work is an execution of the task given by https://github.com/surcyf123/python-task/

## Async API Service for Tao Dividends

This project implements an **asynchronous FastAPI service** to query Tao dividends from the Bittensor blockchain.

### Key Features

- **Authenticated API** – Provides access to blockchain data.
- **Caching** – Stores query results in Redis for 2 minutes.
- **Automated Staking (Optional)** – Uses Twitter sentiment (via Datura.ai & Chutes.ai) to stake/unstake TAO proportionally.
- **Async Processing** – Celery workers handle blockchain queries and sentiment analysis.
- **High-Concurrency Storage** – Uses an async database for historical data.
- **Scalable Architecture** – FastAPI, Redis (cache & broker), Celery (tasks), and Docker for deployment.

## Usage

It is easier to get everything up and running with docker-compose:

```console
docker-compose up -d
```

Or you can set up required services on your own and run locally like this:

```console
uvicorn app.main:app --reload
celery -A app.worker worker --loglevel=info
```

You can run tests with pytest also.

To start required services locally you can use the following Docker commands:

```console
docker run -d --name redis -p 6379:6379 redis
docker run -d --name mongo -p 27017:27017 mongo
```

## API Endpoints

1. **GET /api/v1/tao_dividends**  
   Protected endpoint that returns Tao dividends data for a given subnet and hotkey. Requires `netuid` (subnet ID) and `hotkey` (account ID or public key) as query parameters. Authorization via a bearer token is required.

2. **(Optional) Other Endpoints**
   - POST endpoint for triggering sentiment analysis (if implemented).
   - Health check endpoint (if implemented).
   - Auth login endpoint (if implemented).

## Technical Requirements

- **Asynchronous Design**: Use `asyncio` and non-blocking I/O; all external calls must be async.
- **FastAPI Framework**: Implement REST API with FastAPI, structured under `/api/v1/...`, with auto-docs.
- **Redis & Celery**: Use Redis for caching and as a message broker; offload tasks (sentiment analysis, blockchain actions) to Celery.
- **Database (Async)**:
  - **MongoDB**: Use Motor.
  - **SQL**: Use Tortoise ORM, GINO, or SQLModel/SQLAlchemy (async).
  - Store minimal necessary data (stake history, sentiment cache).
- **Dockerized Setup**:
  - Provide a Dockerfile for FastAPI and Celery workers.
  - Include `docker-compose.yml` for one-command startup.
  - Document setup and environment variables (`.env.example`).
- **Authentication & Security**:
  - Use Bearer tokens or API keys.
  - Manage secrets via environment variables (no hardcoded keys).
- **Code Quality**:
  - Organize modules (`api`, `services`, `db`).
  - Use decorators/middleware for authentication, logging, error handling.
- **Testing (Pytest)**:
  - Write unit and concurrency tests.
  - Validate sentiment analysis, caching, and async behavior.
- **GitHub Best Practices**:
  - Use clear commits, feature branches, and PRs.
  - Keep repository clean with a structured README.

### Performance Goal

The system is designed to handle **~1000 concurrent requests**, ensuring responsiveness with async operations and background tasks.

## Implementation Details

This main objective of this task is to implement one API endpoint that will:

- Authenticate users via a bearer token.
- Accept a subnet ID and a hotkey as query parameters.
- Query the Bittensor blockchain for the latest Tao dividends.
- Cache the results for 2 minutes.

When trade query parameter is set to true, the system should:

- Use Datura.ai to search relevant tweets.
- Use Chutes.ai to analyze the sentiment of the tweets.
- Stake or unstake using Bittensor via testnet.

The system should be designed to handle concurrent requests efficiently, with a focus on performance and scalability. It should return TaoDividends data immediately and perform stake/unstake actions asynchronously.

### Setting up btcli and Getting Testnet Tokens

1. **Install btcli**

   ```console
   pip install btcli
   ```

2. **Create a New Wallet**

   ```console
   btcli wallet new_coldkey --wallet.name default --no_prompt
   btcli wallet new_hotkey --wallet.name default --wallet.hotkey default --no_prompt
   ```

3. **Regenerate Wallet from Seed**
   To access the testnet wallet with 40 TAO:

   ```console
   btcli wallet regen_coldkey --mnemonic "diamond like interest affair safe clarify lawsuit innocent beef van grief color" --wallet.name testnet --no_prompt
   ```

4. **Transfer Testnet Tokens**
   Transfer TAO from the testnet wallet to your default wallet:
   ```console
   btcli wallet transfer --amount 40 --wallet.name testnet --dest_ss58key <your-wallet-ss58-address>
   ```
   Replace `<your-wallet-ss58-address>` with your wallet's SS58 address (you can find it using `btcli wallet overview --wallet.name default`)
