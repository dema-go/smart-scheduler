# Smart Scheduler - 智能排班系统

一个基于 Python FastAPI + Vue 3 的智能排班系统，支持员工信息管理、班次类型管理、智能排班算法和排班结果导出。

## 功能特性

- 员工信息管理（姓名、职位、可工作时间、偏好班次等）
- 班次类型管理（早班、中班、晚班等）
- 智能排班算法（根据员工可用性、偏好、轮换公平性自动生成排班）
- 排班结果查看和手动调整
- 导出功能（支持 CSV/Excel）

## 技术栈

- **后端**: Python 3.10+, FastAPI, SQLAlchemy, SQLite
- **前端**: Vue 3, Vite, Pinia, Element Plus
- **排班算法**: 贪心算法 + 约束满足

## 快速开始

### 前置要求

- Python 3.10+
- Node.js 18+
- pnpm (推荐) 或 npm

### 安装步骤

1. 克隆项目

2. 安装后端依赖
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. 安装前端依赖
```bash
cd frontend
pnpm install
```

### 启动服务

**后端服务** (默认 http://localhost:8000)
```bash
cd backend
python run.py
```

**前端服务** (默认 http://localhost:5173)
```bash
cd frontend
pnpm dev
```

访问 http://localhost:5173 即可使用系统。

## 项目结构

```
smart-scheduler/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API 路由
│   │   ├── models/            # 数据库模型
│   │   ├── schemas/           # Pydantic 模型
│   │   ├── services/         # 业务逻辑
│   │   └── utils/            # 工具函数
│   ├── alembic/               # 数据库迁移
│   ├── requirements.txt       # Python 依赖
│   └── run.py                 # 启动脚本
│
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── components/        # Vue 组件
│   │   ├── views/             # 页面视图
│   │   ├── stores/            # Pinia 状态管理
│   │   └── api/               # API 调用
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

## API 接口文档

启动后端服务后，访问 http://localhost:8000/docs 查看完整 API 文档。

### 主要接口

- `GET /api/employees` - 获取员工列表
- `POST /api/employees` - 创建员工
- `GET /api/shifts` - 获取班次类型列表
- `POST /api/shifts` - 创建班次类型
- `POST /api/schedules/generate` - 生成排班
- `GET /api/schedules` - 获取排班列表
- `PUT /api/schedules/{id}` - 更新排班
- `GET /api/schedules/export` - 导出排班

## 排班算法说明

智能排班算法采用以下策略：

1. **约束过滤**: 首先过滤掉不满足硬约束的员工（如不可用时间、资质不符）
2. **评分排序**: 对满足条件的员工进行评分，评分因素包括：
   - 偏好匹配度（员工偏好的班次）
   - 公平性（分配班次较少的员工优先）
   - 连续工作（避免频繁换班）
3. **贪心分配**: 选择评分最高的员工分配到班次

## 许可证

MIT License
