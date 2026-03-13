# Smart Scheduler - 智能排班系统

一个基于 Python FastAPI + Vue 3 的智能排班系统，支持员工信息管理、班组管理、班次类型管理、智能排班算法和排班结果导出。

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

```bash
git clone https://github.com/dema-go/smart-scheduler.git
cd smart-scheduler
```

2. 安装依赖

```bash
# 使用 Makefile（推荐）
make install

# 或手动安装
cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cd ../frontend && pnpm install
```

### 启动服务

**使用 Makefile（推荐）**
```bash
make dev
```

**或手动启动**

后端服务 (http://localhost:8000)
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

前端服务 (http://localhost:5173)
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
│   │   ├── api/               # API 路由 (employee.py, shift.py, schedule.py, team.py)
│   │   ├── models/            # 数据库模型
│   │   ├── schemas/           # Pydantic 模型
│   │   ├── services/          # 业务逻辑
│   │   └── utils/             # 工具函数
│   ├── requirements.txt       # Python 依赖
│   └── run.py                 # 启动脚本
│
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── components/        # Vue 组件
│   │   ├── views/             # 页面视图 (Dashboard, Employees, Teams, Schedules, Shifts)
│   │   ├── stores/            # Pinia 状态管理
│   │   └── api/               # API 调用
│   ├── package.json
│   └── vite.config.js
│
├── Makefile                    # 常用命令
├── CLAUDE.md                   # 项目开发文档
└── README.md
```

## API 接口文档

启动后端服务后，访问 http://localhost:8000/docs 查看完整 API 文档。

### 主要接口

| 模块 | 接口 | 说明 |
|------|------|------|
| 员工 | `GET/POST /api/employees` | 员工列表/创建 |
| 班组 | `GET/POST /api/teams` | 班组列表/创建 |
| 班次 | `GET/POST /api/shifts` | 班次类型列表/创建 |
| 排班 | `GET /api/schedules` | 排班列表（支持分页） |
| 排班 | `POST /api/schedules/generate` | 智能生成排班 |
| 排班 | `GET /api/schedules/stats` | 排班统计（支持周/月维度） |
| 排班 | `GET /api/schedules/export` | 导出排班（Excel/CSV） |

## 排班算法说明

智能排班算法采用以下策略：

1. **约束过滤**: 首先过滤掉不满足硬约束的员工（如不可用时间、已有排班）
2. **评分排序**: 对满足条件的员工进行评分，评分因素包括：
   - 偏好匹配度（30分）：员工偏好的班次
   - 工作时长均衡（50分）：工作时长较少的员工优先
   - 避免连续同班次（10分）：避免连续工作同一班次
   - 时长差异控制（20分）：防止个别员工时长过高
3. **贪心分配**: 选择评分最高的员工分配到班次
4. **跨天支持**: 自动处理跨天班次（如晚班22:00-次日06:00）

## 常用命令

```bash
make help       # 查看所有命令
make install    # 安装依赖
make dev        # 启动开发模式（前后端）
make backend    # 只启动后端
make frontend   # 只启动前端
make clean      # 停止所有服务
```

## 许可证

MIT License
