from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..core.db import get_db
from ..schemas.finance import GoalCreate, GoalOut
from ..models.finance import Goal, GoalType
from ..services.deps import get_current_user, enforce_shabbat_readonly

router = APIRouter()

@router.get("/", response_model=List[GoalOut])
def list_goals(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Goal).filter(Goal.user_id == user.id).all()

@router.post("/", response_model=GoalOut, dependencies=[Depends(enforce_shabbat_readonly)])
def create_goal(goal_in: GoalCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if goal_in.type not in [t.value for t in GoalType]:
        raise HTTPException(status_code=400, detail="Invalid goal type")
    g = Goal(
        user_id=user.id,
        name=goal_in.name,
        type=GoalType(goal_in.type),
        target_amount=goal_in.target_amount,
        current_amount=goal_in.current_amount,
        due_date=goal_in.due_date,
    )
    db.add(g)
    db.commit()
    db.refresh(g)
    return g
