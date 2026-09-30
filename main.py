from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
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

# Actualizar estado de miembros
def update_members_status(session: Session):
    today = date.today()
    expired_members = session.exec(
        select(Member).where(Member.end_date < today, Member.status != "expired")
    ).all()

    for member in expired_members:
        member.status = "expired"

    if expired_members:
        session.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()

    with Session(engine) as session:
        update_members_status(session)

    yield

app = FastAPI(title="Gym Membership API", lifespan=lifespan)
templates = Jinja2Templates(directory="templates")

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
    
    update_members_status(session)
    
    query = select(Member)

    if status:
        query = query.where(Member.status == status)
    if plan:
        query = query.where(Member.plan == plan)
    if dni:
        query = query.where(Member.dni == dni)

    return session.exec(query).all()

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

#---- Jinja ENDPOINTS ----
# Listado de Miembros
@app.get("/")
async def member_list(request: Request, status: Optional[str] = None, plan: Optional[str] = None, dni: Optional[str] = None, session: Session=Depends(get_session)):
    update_members_status(session)

    query = select(Member)

    if status:
        query = query.where(Member.status == status)
    if plan:
        query = query.where(Member.plan == plan)
    if dni and dni.strip() != "" and dni != "None":
        query = query.where(Member.dni == dni)

    members = session.exec(query).all()
    return templates.TemplateResponse(
        request=request,
        name="member_list.html",
        context={"request": request, "members": members, "status": status, "plan": plan, "dni": dni}
    )

# Detalle de miembro
@app.get("/members/{member_id}/view")
async def member_detail(request: Request, member_id: int, session: Session=Depends(get_session)):
    member = session.get(Member, member_id)
    if not member:
        return templates.TemplateResponse(
                            request=request,
                            name="member_form.html",
                            context={"request": request, "member": member, "edit_mode": False, "error": "Miembro no encontrado"}
                        )
    
    return templates.TemplateResponse(
        request=request,
        name="member_detail.html",
        context={"request": request, "member": member}
    )

# Crear miembro
@app.get("/members_new")
async def member_create_get(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="member_form.html",
        context={"request": request, "edit_mode": False}
    )

@app.post("/members_new")
async def member_create_post(request: Request, session: Session=Depends(get_session)):
    form_data = await request.form()
    member_data = MemberCreate(
        name=form_data.get("name"),
        surname=form_data.get("surname"),
        email=form_data.get("email"),
        phone_number=form_data.get("phone_number"),
        plan=form_data.get("plan"),
        start_date=date.fromisoformat(form_data.get("start_date")),
        end_date=date.fromisoformat(form_data.get("start_date")),
        dni=form_data.get("dni")
    )
    member = Member.model_validate(member_data)
    if member.plan == "mensual":
        member.end_date = member.start_date + timedelta(days=30)
    elif member.plan == "trimestral":
        member.end_date = member.start_date + timedelta(days=90)
    elif member.plan == "anual":
        member.end_date = member.start_date + timedelta(days=365)
    else:
        return templates.TemplateResponse(
                            request=request,
                            name="member_form.html",
                            context={"request": request, "member": member, "edit_mode": False, "error": "Plan invalido"}
                        )
    
    if member.end_date > member.start_date:
        session.add(member)
        session.commit()
        session.refresh(member)
        return templates.TemplateResponse(
            request=request,
            name="member_detail.html",
            context={"request": request, "member": member}
        )
    else:
        return templates.TemplateResponse(
                            request=request,
                            name="member_form.html",
                            context={"request": request, "member": member, "edit_mode": False, "error": "Fecha invalida"}
                        )

# Editar miembro
@app.get("/members/{member_id}/edit")
async def member_edit_get(request: Request, member_id: int, session: Session=Depends(get_session)):
    member = session.get(Member, member_id)
    if not member:
        return templates.TemplateResponse(
                            request=request,
                            name="member_form.html",
                            context={"request": request, "member": member, "edit_mode": False, "error": "Miembro no encontrado"}
                        )
    
    return templates.TemplateResponse(
        request=request,
        name="member_form.html",
        context={"request": request, "member": member, "edit_mode": True}
    )

@app.post("/members/{member_id}/edit")
async def member_edit_post(request: Request, member_id: int, session: Session=Depends(get_session)):
    member = session.get(Member, member_id)
    if not member:
        return templates.TemplateResponse(
                    request=request,
                    name="member_form.html",
                    context={"request": request, "member": member, "edit_mode": False, "error": "Miembro no encontrado"}
                )
    
    form_data = await request.form()
    member_data = MemberUpdate(
        name=form_data.get("name"),
        surname=form_data.get("surname"),
        email=form_data.get("email"),
        phone_number=form_data.get("phone_number"),
        plan=form_data.get("plan"),
        start_date=form_data.get("start_date"),
        dni=form_data.get("dni")
    )
    
    member_data_dict = member_data.model_dump(exclude_unset=True)
    member.sqlmodel_update(member_data_dict)

    if member.plan == "mensual":
        member.end_date = member.start_date + timedelta(days=30)
    elif member.plan == "trimestral":
        member.end_date = member.start_date + timedelta(days=90)
    elif member.plan == "anual":
        member.end_date = member.start_date + timedelta(days=365)
    else:
        return templates.TemplateResponse(
                    request=request,
                    name="member_form.html",
                    context={"request": request, "member": member, "edit_mode": True, "error": "Plan invalido"}
                )
    
    if member.end_date > member.start_date:
        session.add(member)
        session.commit()
        session.refresh(member)
        return templates.TemplateResponse(
            request=request,
            name="member_detail.html",
            context={"request": request, "member": member}
        )
    else:
        return templates.TemplateResponse(
            request=request,
            name="member_form.html",
            context={"request": request, "member": member, "edit_mode": False, "error": "Fecha invalida"}
        )

# Eliminar miembro
@app.post("/members/{member_id}/delete")
async def member_delete(request: Request, member_id: int, session: Session=Depends(get_session)):
    member = session.get(Member, member_id)
    if not member:
        return templates.TemplateResponse(
                    request=request,
                    name="member_form.html",
                    context={"request": request, "member": member, "edit_mode": False, "error": "Miembro no encontrado"}
                )

    session.delete(member)
    session.commit()
    return templates.TemplateResponse(
        request=request,
        name="member_list.html",
        context={"request": request, "members": session.exec(select(Member))}
    )