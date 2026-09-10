from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from typing import Optional, List
from sqlmodel import SQLModel, Field, create_engine, Session, select, col
from datetime import date, datetime, timezone, timedelta

class MemberBase(SQLModel):
    name: str = Field(min_length=2, max_length=50)
    surname: str = Field(min_length=2, max_length=50)
    email: str = Field(unique=True, index=True)
    phone_number: str = Field(max_length=20)
    plan: str
    start_date: date
    end_date: date
    status: str = Field(default="active")  # active, inactive, expired
    dni: Optional[str] = Field(default=None, unique=True, index=True)

class Member(MemberBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MemberCreate(MemberBase):
    pass

class MemberUpdate(SQLModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    plan: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    dni: Optional[str] = None

class MemberRead(MemberBase):
    id: int
    created_at: datetime

engine = create_engine("sqlite:///gym.db")

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="Gym Membership API", lifespan=lifespan)

# CREATE
@app.post("/members/", response_model=MemberRead)
async def create_member(member_data: MemberCreate, session: Session=Depends(get_session)):
    member = Member.model_validate(member_data)
    if member.plan == "mensual":
        member.end_date = member.start_date + timedelta(days=30)
    elif member.plan == "trimestral":
        member.end_date = member.start_date + timedelta(days=90)
    elif member.plan == "anual":
        member.end_date = member.start_date + timedelta(days=365)
    else:
        raise HTTPException(status_code=400, detail="Plan invalido")
    if member.end_date > member.start_date:    
        session.add(member)
        session.commit()
        session.refresh(member)
        return member
    else:
        raise HTTPException(status_code=400, detail="Fecha invalida")

# READ 
@app.get("/members/", response_model=List[MemberRead])
async def read_members(status: Optional[str] = None, plan: Optional[str] = None, dni: Optional[str] = None,session: Session=Depends(get_session)):
    query = select(Member)

    if status:
        query = query.where(Member.status == status)
    if plan:
        query = query.where(Member.plan == plan)
    if dni:
        query = query.where(Member.dni == dni)

    return session.exec(query)

# READ ONE
@app.get("/members/{member_id}", response_model=MemberRead)
async def read_one_member(member_id: int, session: Session=Depends(get_session)):
    member = session.get(Member, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Miembro no Encontrado")
    return member

# UPDATE
@app.put("/members/{member_id}", response_model=MemberRead)
async def update_member(member_id: int, member_data: MemberUpdate, session: Session=Depends(get_session)):
    member = session.get(Member, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Miembro no Encontrado")

    member_data_dict = member_data.model_dump(exclude_unset=True)
    member.sqlmodel_update(member_data_dict)
    
    session.add(member)
    session.commit()
    session.refresh(member)
    return member

# DELETE
@app.delete("/members/{member_id}")
async def delete_member(member_id: int, session: Session=Depends(get_session)):
    member = session.get(Member, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Miembro no encontrado")

    session.delete(member)
    session.commit()
    return {"ok": True, "message": "Miembro eliminado"}