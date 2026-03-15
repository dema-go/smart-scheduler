from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router
from app.models import init_db
from app.config import settings
from app.handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    init_db()
    yield
    # 关闭时可以添加清理逻辑


app = FastAPI(
    title=settings.app_title,
    description="智能排班系统 API",
    version="1.0.0",
    lifespan=lifespan
)

# 注册异常处理器
register_exception_handlers(app)

# CORS 配置 - 从配置文件读取
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router)


@app.get("/")
def root():
    return {"message": "智能排班系统 API", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
