from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.db.database import Base, engine
from app.routers import auth, user, quiz, lfg, friends

# Initialise the FastAPI app
app = FastAPI(title="Tomolink API")

# Automatically create database tables based on SQLAlchemy models
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Enable Cross-Origin Resource Sharing (CORS) for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(quiz.router)
app.include_router(lfg.router)
app.include_router(friends.router)

# GLOBAL EXCEPTION HANDLER: captures any unexpected server error
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("❌ Global exception caught:", repr(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error": str(exc)},
    )

# To allow you to run this file directly: python app/main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
