from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .api.routes import meme_routes, admin_routes

# Initialize Limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI(title="Meme Generator API")

# Add rate limiting exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add Security Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # "https://sub.yourdomain.com", "localhost",  # for local development"127.0.0.1",  # for local development
    allow_credentials=True,
    allow_methods=["*"], # ["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Note: Discussed below
)

# Add Custom Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# Define Routes
@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(meme_routes.router, prefix="/api/v1")
app.include_router(admin_routes.router, prefix="/api/v1/admin")
