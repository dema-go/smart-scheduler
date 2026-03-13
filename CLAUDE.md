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

## Agent Team 开发模式

本项目支持使用 Agent Team 模式进行并行开发，适合多任务、多角色的协作场景。

### 使用场景

当有多个独立任务需要并行处理时，使用 Agent Team 模式可以提高效率：

- 前后端分离开发
- 功能开发 + 测试验证
- 多个 Bug 同时修复

### Team 模式工作流程

```bash
# 1. 创建团队
TeamCreate(team_name="项目名-team", description="任务描述")

# 2. 创建任务
TaskCreate(subject="任务标题", description="详细描述")

# 3. 启动队友（Agent）
Agent(
    description="角色描述",
    name="角色名",  # 如 backend-dev, frontend-dev, tester
    prompt="详细任务说明",
    subagent_type="general-purpose",
    team_name="项目名-team"
)

# 4. 分配任务
TaskUpdate(taskId="1", owner="角色名")

# 5. 设置任务依赖（可选）
TaskUpdate(taskId="3", addBlockedBy=["1", "2"])  # 任务3依赖1和2完成

# 6. 等待队友完成任务（自动接收消息）

# 7. 关闭队友
SendMessage(type="shutdown_request", recipient="角色名")

# 8. 删除团队
TeamDelete()
```

### 角色分工示例

| 角色 | 职责 | 任务类型 |
|------|------|----------|
| backend-dev | 后端 API 开发、数据库模型修改 | 后端相关任务 |
| frontend-dev | 前端页面、组件开发 | 前端相关任务 |
| tester | 功能测试、API 验证 | 测试验证任务 |

### 代码提交流程

完成开发和测试后，使用 Skill 工具提交代码：

```bash
/commit  # 或使用 Skill tool 调用 commit skill
```

### 注意事项

1. 任务之间设置依赖关系，确保测试在开发完成后进行
2. 队友之间通过 SendMessage 通信
3. 完成后记得关闭所有队友并删除团队
4. 重要修改需要经过测试验证后再提交
