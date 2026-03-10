from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router
from app.models import init_db
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    description="智能排班系统 API",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
@app.on_event("startup")
def startup_event():
    init_db()

# 注册路由
app.include_router(api_router)


@app.get("/")
def root():
    return {"message": "智能排班系统 API", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
