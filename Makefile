.PHONY: help install dev backend frontend all clean migrate test

# 配置变量 - 可通过环境变量覆盖
BACKEND_PORT ?= 8000
FRONTEND_PORT ?= 5173
BACKEND_HOST ?= 0.0.0.0

# 自动检测本机 IP（macOS/Linux）
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
    LOCAL_IP := $(shell ipconfig getifaddr en0 2>/dev/null || echo "127.0.0.1")
else
    LOCAL_IP := $(shell hostname -I 2>/dev/null | cut -d' ' -f1 || echo "127.0.0.1")
endif

help:
	@echo "智能排班系统 - 启动命令"
	@echo ""
	@echo "make install    - 安装依赖 (后端 + 前端)"
	@echo "make dev        - 开发模式 (前后端都启动)"
	@echo "make backend    - 只启动后端 (端口 $(BACKEND_PORT))"
	@echo "make frontend   - 只启动前端 (端口 $(FRONTEND_PORT))"
	@echo "make all        - 前后端都启动 (后台运行)"
	@echo "make clean      - 停止所有服务"
	@echo ""
	@echo "数据库迁移命令:"
	@echo "make migrate    - 生成并应用数据库迁移"
	@echo "make migrate-gen - 只生成迁移文件 (不应用)"
	@echo "make migrate-up - 应用待执行的迁移"
	@echo "make migrate-down - 回滚最后一次迁移"
	@echo ""
	@echo "测试命令:"
	@echo "make test       - 运行所有测试"
	@echo ""
	@echo "配置变量 (通过环境变量覆盖):"
	@echo "  BACKEND_PORT  - 后端端口 (默认: 8000)"
	@echo "  FRONTEND_PORT - 前端端口 (默认: 5173)"
	@echo "  BACKEND_HOST  - 后端监听地址 (默认: 0.0.0.0)"
	@echo ""

install:
	@echo "安装后端依赖..."
	@cd backend && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	@echo "安装前端依赖..."
	@cd frontend && npm install

dev: clean
	@echo "启动开发模式 (前后端)..."
	@echo "启动后端服务 (端口 $(BACKEND_PORT))..."
	@cd backend && source venv/bin/activate && PYTHONPATH=. nohup uvicorn app.main:app --host $(BACKEND_HOST) --port $(BACKEND_PORT) --reload > ../backend.log 2>&1 &
	@sleep 3
	@echo "启动前端服务 (端口 $(FRONTEND_PORT))..."
	@cd frontend && VITE_API_TARGET=http://127.0.0.1:$(BACKEND_PORT) nohup npm run dev -- --host --port $(FRONTEND_PORT) > ../frontend.log 2>&1 &
	@echo "启动完成!"
	@echo "本机访问: http://localhost:$(FRONTEND_PORT)"
	@echo "外部访问: http://$(LOCAL_IP):$(FRONTEND_PORT)"

backend: clean
	@echo "启动后端服务..."
	@cd backend && source venv/bin/activate && PYTHONPATH=. nohup uvicorn app.main:app --host $(BACKEND_HOST) --port $(BACKEND_PORT) --reload > ../backend.log 2>&1 &
	@sleep 3
	@echo "后端已启动: http://127.0.0.1:$(BACKEND_PORT)"

frontend:
	@echo "启动前端服务..."
	@(cd frontend && VITE_API_TARGET=http://127.0.0.1:$(BACKEND_PORT) nohup npm run dev -- --port $(FRONTEND_PORT) > frontend.log 2>&1 &)
	@echo "前端已启动: http://localhost:$(FRONTEND_PORT)"

all: clean
	@echo "以后台模式启动前后端服务..."
	@cd backend && source venv/bin/activate && PYTHONPATH=. nohup uvicorn app.main:app --host $(BACKEND_HOST) --port $(BACKEND_PORT) > ../backend.log 2>&1 &
	@sleep 3
	@cd frontend && VITE_API_TARGET=http://127.0.0.1:$(BACKEND_PORT) nohup npm run dev -- --port $(FRONTEND_PORT) > ../frontend.log 2>&1 &
	@echo "后端已启动: http://localhost:$(BACKEND_PORT)"
	@echo "前端已启动: http://localhost:$(FRONTEND_PORT)"

clean:
	@echo "停止所有服务..."
	@pkill -f "uvicorn app.main:app" 2>/dev/null || true
	@pkill -f "vite" 2>/dev/null || true
	@echo "服务已停止"

# 数据库迁移
migrate:
	@echo "生成数据库迁移..."
	@cd backend && source venv/bin/activate && alembic revision --autogenerate -m "auto_migration"
	@echo "应用迁移..."
	@cd backend && source venv/bin/activate && alembic upgrade head
	@echo "迁移完成!"

migrate-gen:
	@echo "生成迁移文件..."
	@cd backend && source venv/bin/activate && alembic revision --autogenerate -m "auto_migration"
	@echo "迁移文件已生成，请检查后使用 'make migrate-up' 应用"

migrate-up:
	@echo "应用待执行的迁移..."
	@cd backend && source venv/bin/activate && alembic upgrade head
	@echo "迁移已应用!"

migrate-down:
	@echo "回滚最后一次迁移..."
	@cd backend && source venv/bin/activate && alembic downgrade -1
	@echo "迁移已回滚!"

# 测试
test:
	@echo "运行测试..."
	@cd backend && source venv/bin/activate && python -m pytest tests/ -v
