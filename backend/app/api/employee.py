from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.models import get_db
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse

router = APIRouter(prefix="/api/employees", tags=["员工管理"])


def _add_team_name(employee):
    """为员工对象添加 team_name 字段"""
    result = EmployeeResponse.model_validate(employee)
    result.team_name = employee.team.name if employee.team else None
    return result


@router.get("", response_model=List[EmployeeResponse])
def get_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取员工列表"""
    employees = db.query(Employee).options(
        joinedload(Employee.team)
    ).filter(Employee.is_active == True).offset(skip).limit(limit).all()
    return [_add_team_name(emp) for emp in employees]


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    """获取单个员工信息"""
    employee = db.query(Employee).options(
        joinedload(Employee.team)
    ).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="员工不存在")
    return _add_team_name(employee)


@router.post("", response_model=EmployeeResponse)
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    """创建员工"""
    db_employee = Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    # 重新加载包含 team 关联
    db_employee = db.query(Employee).options(
        joinedload(Employee.team)
    ).filter(Employee.id == db_employee.id).first()
    return _add_team_name(db_employee)


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(employee_id: int, employee: EmployeeUpdate, db: Session = Depends(get_db)):
    """更新员工信息"""
    db_employee = db.query(Employee).options(
        joinedload(Employee.team)
    ).filter(Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="员工不存在")

    for key, value in employee.model_dump(exclude_unset=True).items():
        setattr(db_employee, key, value)

    db.commit()
    # 重新加载包含 team 关联
    db_employee = db.query(Employee).options(
        joinedload(Employee.team)
    ).filter(Employee.id == employee_id).first()
    return _add_team_name(db_employee)


@router.delete("/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    """删除员工（软删除）"""
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="员工不存在")

    db_employee.is_active = False
    db.commit()
    return {"message": "员工已删除"}
