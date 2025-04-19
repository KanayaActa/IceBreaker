from fastapi import FastAPI
from app.routers import user, category, rating, match, result, ranking, auth, graph
from fastapi.middleware.cors import CORSMiddleware
import asyncio


# FastAPIインスタンス（タイトルや説明込みで1つだけ作成）
app = FastAPI(
    title="IceBreaker API",
    description="API for IceBreaker application",
    version="1.0.0"
)

# CORSミドルウェアを追加

# CORS設定
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 各ルーターを登録
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(category.router)
app.include_router(rating.router)
app.include_router(match.router)
app.include_router(result.router)
app.include_router(ranking.router)
app.include_router(graph.router)

# ルートエンドポイント
@app.get("/")
def read_root():
    return {"message": "Welcome to IceBreaker API!"}
