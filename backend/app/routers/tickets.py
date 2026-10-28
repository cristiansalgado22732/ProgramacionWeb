from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Ticket
from ..schemas import TicketIn, TicketOut, TicketUpdate

router = APIRouter(prefix="/tickets", tags=["tickets"])
DB = Annotated[Session, Depends(get_db)]

# TEMPORAL: mientras no hay login, todos los tickets quedan a nombre del admin (id 1).
# En la iteración 05 se reemplaza por el usuario autenticado.
TEMP_AUTHOR_ID = 1


@router.get("", response_model=list[TicketOut])
def list_tickets(db: DB):
    query = select(Ticket).order_by(Ticket.created_at.desc())
    return db.scalars(query).all()


@router.post("", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
def create_ticket(data: TicketIn, db: DB):
    ticket = Ticket(**data.model_dump(), author_id=TEMP_AUTHOR_ID)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.patch("/{ticket_id}", response_model=TicketOut)
def update_ticket(ticket_id: int, data: TicketUpdate, db: DB):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ticket no encontrado")
    ticket.status = data.status
    db.commit()
    db.refresh(ticket)
    return ticket


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(ticket_id: int, db: DB):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ticket no encontrado")
    db.delete(ticket)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)