from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models import get_db
from app.models.shift import ShiftType
from app.schemas.shift import ShiftTypeCreate, ShiftTypeUpdate, ShiftTypeResponse

router = APIRouter(prefix="/api/shifts", tags=["班次管理"])


@router.get("", response_model=List[ShiftTypeResponse])
def get_shifts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取班次类型列表"""
    shifts = db.query(ShiftType).filter(ShiftType.is_active == True).offset(skip).limit(limit).all()
    return shifts


@router.get("/{shift_id}", response_model=ShiftTypeResponse)
def get_shift(shift_id: int, db: Session = Depends(get_db)):
    """获取单个班次类型"""
    shift = db.query(ShiftType).filter(ShiftType.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="班次类型不存在")
    return shift


@router.post("", response_model=ShiftTypeResponse)
def create_shift(shift: ShiftTypeCreate, db: Session = Depends(get_db)):
    """创建班次类型"""
    db_shift = ShiftType(**shift.model_dump())
    db.add(db_shift)
    db.commit()
    db.refresh(db_shift)
    return db_shift


@router.put("/{shift_id}", response_model=ShiftTypeResponse)
def update_shift(shift_id: int, shift: ShiftTypeUpdate, db: Session = Depends(get_db)):
    """更新班次类型"""
    db_shift = db.query(ShiftType).filter(ShiftType.id == shift_id).first()
    if not db_shift:
        raise HTTPException(status_code=404, detail="班次类型不存在")

    for key, value in shift.model_dump(exclude_unset=True).items():
        setattr(db_shift, key, value)

    db.commit()
    db.refresh(db_shift)
    return db_shift


@router.delete("/{shift_id}")
def delete_shift(shift_id: int, db: Session = Depends(get_db)):
    """删除班次类型（软删除）"""
    db_shift = db.query(ShiftType).filter(ShiftType.id == shift_id).first()
    if not db_shift:
        raise HTTPException(status_code=404, detail="班次类型不存在")

    db_shift.is_active = False
    db.commit()
    return {"message": "班次类型已删除"}
