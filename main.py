# app/main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.db.database import Base, engine
from app.routers import auth, user, quiz, lfg, friends, suggestions, feedback, dashboard, game_profiles, matchmaking

# ✅ Initialise the FastAPI app
app = FastAPI(title="Tomolink API")

# ⚠️ REMOVE this in production: drops everything on startup
# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# ✅ Enable CORS for frontend (React Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # adjust if deployed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Register all API routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(quiz.router)
app.include_router(lfg.router)
app.include_router(friends.router)
app.include_router(suggestions.router)
app.include_router(feedback.router)
app.include_router(dashboard.router)
app.include_router(game_profiles.router)
app.include_router(matchmaking.router)

# ✅ Health check root route
@app.get("/")
async def root():
    return {"message": "Tomolink API is running 🚀"}

# ✅ Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("❌ Global exception caught:", repr(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error": str(exc)},
    )

# ✅ Optional logging middleware for development
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"➡️ Request: {request.method} {request.url}")
    response = await call_next(request)
    print(f"⬅️ Response: {response.status_code}")
    return response

# ✅ Entry point for running directly: `python app/main.py`
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
