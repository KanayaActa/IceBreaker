from fastapi import FastAPI
from app.routers import user, category, rating, match, result, ranking

app = FastAPI(
    title="IceBreaker API",
    description="API for IceBreaker application",
    version="1.0.0"
)

# Include all routers
app.include_router(user.router)
app.include_router(category.router)
app.include_router(rating.router)
app.include_router(match.router)
app.include_router(result.router)
app.include_router(ranking.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to IceBreaker API!"}
