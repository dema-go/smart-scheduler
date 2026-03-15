# Smart Scheduler - 智能排班系统

一个基于 Python FastAPI + Vue 3 的智能排班系统，支持员工信息管理、班组管理、班次类型管理、智能排班算法和排班结果导出。

[![CI/CD](https://github.com/dema-go/smart-scheduler/actions/workflows/ci.yml/badge.svg)](https://github.com/dema-go/smart-scheduler/actions/workflows/ci.yml)

## 功能特性

- **员工管理**：员工信息管理（姓名、职位、所属班组、可工作时间、偏好班次等）
- **班组管理**：支持按班组进行员工分组和排班
- **班次管理**：班次类型管理（早班、中班、晚班等，支持自定义时长和颜色）
- **Dashboard 首页**：统计卡片、今日排班、快捷操作、周/月维度排行统计
- **排班日历视图**：月历展示排班信息、月份切换、班次筛选
- **排班列表**：支持分页、搜索、批量删除
- **智能排班算法**：根据员工可用性、偏好、工作时长均衡自动生成排班
- **排班统计**：员工周/月排班天数、班次分布、工作时长统计
- **导出功能**：支持 Excel 和 CSV 格式导出

## 技术栈

| 类型 | 技术 |
|------|------|
| 后端 | Python 3.11+, FastAPI, SQLAlchemy 2.0, SQLite, Alembic |
| 前端 | Vue 3, Vite, Pinia, Element Plus, TypeScript |
| 测试 | pytest, httpx (43 个测试用例) |
| 部署 | Docker, docker-compose, GitHub Actions CI/CD |
| 安全 | CORS 配置, API 限流 (slowapi) |

## 快速开始

### 前置要求

- Python 3.11+
- Node.js 18+
- pnpm (推荐) 或 npm

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/dema-go/smart-scheduler.git
cd smart-scheduler

# 2. 安装依赖
make install
```

### 启动服务

```bash
# 开发模式（推荐）
make dev

# 访问
# 前端: http://localhost:5173
# 后端: http://localhost:8000
# API文档: http://localhost:8000/docs
```

## 常用命令

```bash
make help         # 查看所有命令
make install      # 安装依赖
make dev          # 启动开发模式
make test         # 运行测试
make migrate      # 数据库迁移
make clean        # 停止服务

# 配置变量
BACKEND_PORT=8000 FRONTEND_PORT=5173 make dev
```

## Docker 部署

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

## 项目结构

```
smart-scheduler/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API 路由
│   │   ├── models/            # 数据库模型
│   │   ├── schemas/           # Pydantic 模型
│   │   ├── services/          # 业务逻辑
│   │   ├── exceptions.py      # 自定义异常
│   │   ├── handlers.py        # 异常处理器
│   │   ├── logger.py          # 日志配置
│   │   └── rate_limit.py      # API 限流
│   ├── migrations/            # 数据库迁移
│   ├── tests/                 # 测试套件
│   └── Dockerfile
│
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── components/        # Vue 组件
│   │   ├── views/             # 页面视图
│   │   ├── stores/            # Pinia 状态管理
│   │   └── api/               # API 调用
│   └── Dockerfile
│
├── .github/workflows/         # CI/CD 配置
├── Makefile                    # 常用命令
├── docker-compose.yml          # Docker 编排
├── CLAUDE.md                   # 开发文档
└── README.md
```

## API 接口

| 模块 | 接口 | 说明 |
|------|------|------|
| 员工 | `GET/POST /api/employees` | 员工列表/创建 |
| 班组 | `GET/POST /api/teams` | 班组列表/创建 |
| 班次 | `GET/POST /api/shifts` | 班次类型列表/创建 |
| 排班 | `GET /api/schedules` | 排班列表（分页、搜索） |
| 排班 | `POST /api/schedules/generate` | 智能生成排班 |
| 排班 | `GET /api/schedules/stats` | 排班统计 |
| 排班 | `GET /api/schedules/export` | 导出排班 |

完整 API 文档: http://localhost:8000/docs

## 排班算法

1. **约束过滤** - 过滤不满足硬约束的员工
2. **评分排序** - 偏好匹配(25分) + 工作均衡(120分) + 避免连续同班次(10分)
3. **贪心分配** - 选择评分最高的员工
4. **跨天支持** - 自动处理跨天班次

## 测试

```bash
make test
# 43 个测试用例，覆盖 API 和排班算法
```

## 数据库迁移

```bash
make migrate      # 生成并应用迁移
make migrate-up   # 应用迁移
make migrate-down # 回滚迁移
```

## 许可证

MIT License
