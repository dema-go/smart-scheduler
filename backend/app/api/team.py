from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import get_db
from app.models.team import Team
from app.models.employee import Employee
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse, TeamWithEmployeeCount

router = APIRouter(prefix="/api/teams", tags=["班组管理"])


@router.get("", response_model=List[TeamWithEmployeeCount])
def get_teams(
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """获取班组列表"""
    query = db.query(Team)

    if is_active is not None:
        query = query.filter(Team.is_active == is_active)

    teams = query.order_by(Team.id).all()

    # 添加员工数量统计
    result = []
    for team in teams:
        employee_count = db.query(Employee).filter(
            Employee.team_id == team.id,
            Employee.is_active == True
        ).count()
        result.append(TeamWithEmployeeCount(
            id=team.id,
            name=team.name,
            description=team.description,
            is_active=team.is_active,
            employee_count=employee_count
        ))

    return result


@router.get("/{team_id}", response_model=TeamWithEmployeeCount)
def get_team(team_id: int, db: Session = Depends(get_db)):
    """获取单个班组详情"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="班组不存在")

    # 统计员工数量
    employee_count = db.query(Employee).filter(
        Employee.team_id == team.id,
        Employee.is_active == True
    ).count()

    return TeamWithEmployeeCount(
        id=team.id,
        name=team.name,
        description=team.description,
        is_active=team.is_active,
        employee_count=employee_count
    )


@router.get("/{team_id}/employees", response_model=List[dict])
def get_team_employees(team_id: int, db: Session = Depends(get_db)):
    """获取班组下的员工列表"""
    # 先检查班组是否存在
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="班组不存在")

    employees = db.query(Employee).filter(
        Employee.team_id == team_id,
        Employee.is_active == True
    ).all()

    return [
        {
            "id": emp.id,
            "name": emp.name,
            "position": emp.position,
            "phone": emp.phone,
            "email": emp.email
        }
        for emp in employees
    ]


@router.post("", response_model=TeamResponse)
def create_team(team: TeamCreate, db: Session = Depends(get_db)):
    """创建班组"""
    # 检查名称是否已存在
    existing = db.query(Team).filter(Team.name == team.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="班组名称已存在")

    db_team = Team(**team.model_dump())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team


@router.put("/{team_id}", response_model=TeamResponse)
def update_team(team_id: int, team: TeamUpdate, db: Session = Depends(get_db)):
    """更新班组"""
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="班组不存在")

    # 检查名称是否与其他班组重复
    if team.name and team.name != db_team.name:
        existing = db.query(Team).filter(
            Team.name == team.name,
            Team.id != team_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="班组名称已存在")

    for key, value in team.model_dump(exclude_unset=True).items():
        setattr(db_team, key, value)

    db.commit()
    db.refresh(db_team)
    return db_team


@router.delete("/{team_id}")
def delete_team(team_id: int, db: Session = Depends(get_db)):
    """删除班组"""
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="班组不存在")

    # 检查是否有员工关联
    employee_count = db.query(Employee).filter(Employee.team_id == team_id).count()
    if employee_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"该班组下有 {employee_count} 名员工，无法删除。请先移除员工或禁用班组。"
        )

    db.delete(db_team)
    db.commit()
    return {"message": "班组已删除"}
