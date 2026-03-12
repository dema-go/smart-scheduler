.PHONY: help install dev backend frontend all clean

help:
	@echo "智能排班系统 - 启动命令"
	@echo ""
	@echo "make install    - 安装依赖 (后端 + 前端)"
	@echo "make dev        - 开发模式 (前后端都启动)"
	@echo "make backend    - 只启动后端 (端口 8000)"
	@echo "make frontend   - 只启动前端 (端口 5173)"
	@echo "make all        - 前后端都启动 (后台运行)"
	@echo "make clean      - 停止所有服务"
	@echo ""

install:
	@echo "安装后端依赖..."
	cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	@echo "安装前端依赖..."
	cd frontend && pnpm install

dev: backend frontend

backend:
	@echo "启动后端服务..."
	@cd backend && . venv/bin/activate && PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

frontend:
	@echo "启动前端服务..."
	@cd frontend && pnpm dev

all:
	@echo "以后台模式启动前后端服务..."
	@cd backend && . venv/bin/activate && PYTHONPATH=. nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
	@cd frontend && nohup pnpm dev > frontend.log 2>&1 &
	@echo "后端已启动: http://localhost:8000"
	@echo "前端已启动: http://localhost:5173"

clean:
	@echo "停止所有服务..."
	@pkill -f "uvicorn app.main:app" 2>/dev/null || true
	@pkill -f "vite" 2>/dev/null || true
	@echo "服务已停止"
