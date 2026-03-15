# Smart Scheduler - 智能排班系统

## 项目概述

这是一个基于 Python FastAPI + Vue 3 的智能排班系统，支持员工信息管理、班组管理、班次类型管理、智能排班算法和排班结果导出。

## 技术栈

- **后端**: Python 3.11+, FastAPI, SQLAlchemy 2.0, SQLite, Alembic
- **前端**: Vue 3, Vite, Pinia, Element Plus, TypeScript
- **排班算法**: 贪心算法 + 约束满足
- **测试**: pytest, httpx
- **部署**: Docker, docker-compose, GitHub Actions CI/CD

## 项目结构

```
smart-scheduler/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API 路由
│   │   │   ├── employee.py    # 员工管理
│   │   │   ├── shift.py       # 班次管理
│   │   │   ├── schedule.py    # 排班管理
│   │   │   └── team.py        # 班组管理
│   │   ├── models/            # 数据库模型 (SQLAlchemy 2.0)
│   │   ├── schemas/           # Pydantic 模型
│   │   ├── services/          # 业务逻辑
│   │   │   ├── scheduler.py   # 排班算法
│   │   │   └── stats.py       # 统计服务
│   │   ├── exceptions.py      # 自定义异常
│   │   ├── handlers.py        # 异常处理器
│   │   ├── logger.py          # 日志配置
│   │   ├── rate_limit.py      # API 限流
│   │   └── config.py          # 配置管理
│   ├── migrations/            # Alembic 数据库迁移
│   ├── tests/                 # 测试套件 (43 个测试)
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── alembic.ini
│   └── Dockerfile
│
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── components/        # Vue 组件
│   │   ├── views/             # 页面视图
│   │   ├── stores/            # Pinia 状态管理
│   │   │   ├── employee.ts
│   │   │   ├── shift.ts
│   │   │   └── schedule.ts
│   │   └── api/               # API 调用
│   ├── package.json
│   ├── vite.config.js
│   ├── Dockerfile
│   └── nginx.conf
│
├── .github/
│   └── workflows/
│       └── ci.yml             # CI/CD 工作流
│
├── Makefile                    # 常用命令
├── docker-compose.yml          # Docker 编排
├── CLAUDE.md                   # 项目开发文档
└── README.md
```

## 启动命令

### 开发模式

```bash
# 使用 Makefile（推荐）
make dev        # 启动开发模式（前后端）

# 或手动启动
make backend    # 只启动后端 (http://localhost:8000)
make frontend   # 只启动前端 (http://localhost:5173)
```

### 配置变量

```bash
# 可通过环境变量覆盖默认配置
BACKEND_PORT=8000 FRONTEND_PORT=5173 make dev
```

### Docker 部署

```bash
docker-compose up -d
# 前端: http://localhost
# 后端: http://localhost:8000
```

## 关键功能

1. **员工管理** - 姓名、职位、班组、可用时间、偏好班次
2. **班组管理** - 按班组分组和排班
3. **班次管理** - 自定义时长、颜色、所需人数
4. **Dashboard** - 统计卡片、今日排班、周/月统计
5. **排班日历** - 月历展示、月份切换
6. **智能排班** - 自动生成，考虑偏好、均衡、约束
7. **排班统计** - 天数、班次分布、工作时长
8. **导出功能** - Excel/CSV 格式

## 测试

```bash
# 运行所有测试
make test

# 或手动运行
cd backend && source venv/bin/activate && pytest tests/ -v
```

测试覆盖：
- API 接口测试 (员工、班次、排班、班组)
- 排班算法测试 (时长计算、公平性、约束满足)
- 异常处理测试

## 数据库迁移

```bash
make migrate      # 生成并应用迁移
make migrate-gen  # 只生成迁移文件
make migrate-up   # 应用待执行的迁移
make migrate-down # 回滚最后一次迁移
```

## 排班算法说明

智能排班算法采用以下策略：

1. **约束过滤** - 过滤不满足硬约束的员工
2. **评分排序** - 偏好匹配(25分) + 工作均衡(120分) + 避免连续同班次(10分)
3. **贪心分配** - 选择评分最高的员工
4. **跨天支持** - 自动处理跨天班次

## 主要 API 接口

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

## 代码质量

- **测试覆盖**: 43 个测试用例
- **异常处理**: 统一错误响应格式
- **API 限流**: slowapi 保护关键接口
- **日志系统**: RotatingFileHandler，分离错误日志
- **类型注解**: 关键函数完整类型提示

## Agent Team 开发模式

本项目支持使用 Agent Team 模式进行并行开发：

```bash
# 1. 创建团队
TeamCreate(team_name="scheduler-team", description="任务描述")

# 2. 创建任务
TaskCreate(subject="任务标题", description="详细描述")

# 3. 启动队友
Agent(description="后端开发", name="backend-dev", prompt="...", subagent_type="general-purpose")

# 4. 分配任务
TaskUpdate(taskId="1", owner="backend-dev")

# 5. 完成后关闭
SendMessage(type="shutdown_request", recipient="backend-dev")
TeamDelete()
```

## 任务驱动开发流程

本项目采用任务驱动开发模式，每次会话从 `TODO.md` 中读取一个任务进行完成。

### 任务执行步骤

1. **读取任务**: 使用 Read 工具读取 `TODO.md`，找到第一个未完成的任务（标记为 `[ ]`）
2. **理解任务**: 阅读任务描述、相关文件和优先级
3. **执行开发**: 按任务要求完成开发工作
4. **验证测试**: 运行 `make test` 确保所有测试通过
5. **更新状态**: 将 TODO.md 中的任务状态从 `[ ]` 改为 `[x]`
6. **更新文档**: 同步更新 CLAUDE.md 和 README.md（如有必要）
7. **提交代码**: 提交变更并推送到远程仓库

### 任务优先级

- **P0**: 关键修复 - 必须立即处理
- **P1**: 重要优化 - 影响核心功能
- **P2**: 增强功能 - 提升代码质量
- **P3**: 可选优化 - 改善用户体验
- **F**: 未来功能 - 后续迭代考虑

### 示例工作流

```bash
# 1. 读取 TODO.md 找到第一个 [ ] 任务
# 2. 执行任务开发
# 3. 运行测试验证
make test

# 4. 更新 TODO.md 将 [ ] 改为 [x]
# 5. 更新相关文档（如果任务影响了项目结构或功能）
# 6. 提交并推送
git add -A && git commit -m "feat: 完成任务描述"
git push origin main
```

## 代码提交流程

**重要**: 每次修改完推送代码前都要更新 CLAUDE.md 和 README.md

```bash
# 1. 更新文档
# 2. 提交代码
git add -A && git commit -m "描述"
# 3. 推送
git push origin main
```

## 注意事项

1. CORS 配置从环境变量读取，生产环境需配置 `CORS_ORIGINS`
2. API 限流默认开启，生成排班 5次/分钟，导出 10次/分钟
3. 日志文件位于 `backend/logs/` 目录
