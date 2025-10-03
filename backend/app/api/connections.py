from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.db import get_db
from ..services.deps import get_current_user
from ..models.connections import ConnectedAccount
from pydantic import BaseModel

router = APIRouter()


class ConnectionCreate(BaseModel):
    provider: str
    display_name: str | None = None


@router.get('/')
def list_connections(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = db.query(ConnectedAccount).filter(ConnectedAccount.user_id == user.id).all()
    return [
        {
            'id': r.id,
            'provider': r.provider,
            'display_name': r.display_name,
            'status': r.status,
            'external_id': r.external_id,
        }
        for r in rows
    ]


@router.post('/')
def add_connection(payload: ConnectionCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    row = ConnectedAccount(user_id=user.id, provider=payload.provider, display_name=payload.display_name or payload.provider)
    db.add(row)
    db.commit()
    db.refresh(row)
    return {'id': row.id}


@router.delete('/{conn_id}')
def remove_connection(conn_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    row = db.query(ConnectedAccount).filter(ConnectedAccount.id == conn_id, ConnectedAccount.user_id == user.id).first()
    if not row:
        raise HTTPException(status_code=404, detail='Not found')
    db.delete(row)
    db.commit()
    return {'ok': True}
