from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Tao Dividends API",
    description="Asynchronous FastAPI service for querying Tao dividends from the Bittensor blockchain",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/")
async def root():
    return {"message": "Welcome to Tao Dividends API"}


@app.get("/api/v1/tao_dividends")
async def get_tao_dividends(
    netuid: int,
    hotkey: str,
    trade: bool = False,
    token: str = Depends(oauth2_scheme)
):
    # TODO: Implement the following:
    # 1. Validate token
    # 2. Query blockchain for Tao dividends
    # 3. Cache results in Redis
    # 4. If trade=True, trigger sentiment analysis tasks
    return {"message": "Not implemented yet"}