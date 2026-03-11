# Smart Scheduler - 智能排班系统

## 项目概述

这是一个基于 Python FastAPI + Vue 3 的智能排班系统，支持员工信息管理、班次类型管理、智能排班算法和排班结果导出。

## 技术栈

- **后端**: Python 3.10+, FastAPI, SQLAlchemy, SQLite
- **前端**: Vue 3, Vite, Pinia, Element Plus
- **排班算法**: 贪心算法 + 约束满足

## 项目结构

```
smart-scheduler/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API 路由 (employee.py, shift.py, export.py)
│   │   ├── models/            # 数据库模型 (employee.py, shift.py, schedule.py)
│   │   ├── schemas/           # Pydantic 模型
│   │   ├── services/          # 业务逻辑
│   │   └── utils/             # 工具函数
│   ├── requirements.txt       # Python 依赖
│   └── run.py                 # 启动脚本
│
└── frontend/                   # 前端应用
    ├── src/
    │   ├── components/        # Vue 组件
    │   ├── views/             # 页面视图
    │   ├── stores/            # Pinia 状态管理
    │   └── api/               # API 调用
    ├── package.json
    └── vite.config.js
```

## 启动命令

- 后端: `cd backend && python run.py` (http://localhost:8000)
- 前端: `cd frontend && pnpm dev` (http://localhost:5173)
- API 文档: http://localhost:8000/docs

## 关键功能

1. 员工信息管理（姓名、职位、可工作时间、偏好班次等）
2. 班次类型管理（早班、中班、晚班等，支持自定义时长和颜色）
3. Dashboard 首页：统计卡片、今日排班、快捷操作
4. 排班日历视图：月历展示、月份切换
5. 智能排班算法：根据员工可用性、偏好、工作时长均衡自动生成排班
6. 排班统计：员工月度排班天数、班次分布
7. 导出功能（支持 CSV）

## 排班算法说明

智能排班算法采用以下策略：
1. **约束过滤**: 首先过滤掉不满足硬约束的员工
2. **评分排序**: 对满足条件的员工进行评分（偏好匹配度、工作时长均衡、避免连续同班次等）
3. **贪心分配**: 选择评分最高的员工分配到班次
4. **跨天支持**: 自动处理跨天班次

## 主要 API 接口

- `GET /api/employees` - 获取员工列表
- `POST /api/employees` - 创建员工
- `GET /api/shifts` - 获取班次类型列表
- `POST /api/shifts` - 创建班次类型
- `POST /api/schedules/generate` - 生成排班
- `GET /api/schedules` - 获取排班列表
- `PUT /api/schedules/{id}` - 更新排班
- `GET /api/schedules/export` - 导出排班
