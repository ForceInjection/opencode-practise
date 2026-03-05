"""服务器入口 (FastAPI)"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .database import init_db
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    init_db()
    print("🚀 Task Manager API 运行在 http://localhost:3000")
    yield
    # 关闭时清理（如需要）


app = FastAPI(
    title="Task Manager API",
    description="OpenCode 实战案例：任务管理 REST API (Python 版)",
    version="1.0.0",
    lifespan=lifespan,
)


# 健康检查端点
@app.get("/")
def health_check():
    """健康检查"""
    return {"message": "Task Manager API is running"}


# 注册路由
app.include_router(router)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局错误处理"""
    is_prod = os.getenv("ENV") == "production"
    return JSONResponse(
        status_code=500,
        content={"error": "服务器内部错误" if is_prod else str(exc)},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=3000, reload=True)
