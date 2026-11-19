import os, secrets, hashlib, hmac
from datetime import datetime
from decimal import Decimal
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Numeric, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

BASE=os.path.dirname(__file__)
DATABASE_URL=os.getenv('DATABASE_URL','sqlite:///'+os.path.join(BASE,'webcore.db'))
if DATABASE_URL.startswith('postgres://'): DATABASE_URL='postgresql://'+DATABASE_URL[len('postgres://'):]
engine=create_engine(DATABASE_URL,connect_args={'check_same_thread':False} if DATABASE_URL.startswith('sqlite') else {},pool_pre_ping=True)
Session=sessionmaker(bind=engine)
Base=declarative_base()
class Entry(Base):
    __tablename__='entries'
    id=Column(Integer,primary_key=True)
    kind=Column(String(20),nullable=False)
    description=Column(String(200),nullable=False)
    category=Column(String(80),nullable=False)
    amount=Column(Numeric(12,2),nullable=False)
    created=Column(DateTime,default=datetime.utcnow)
class Lead(Base):
    __tablename__='leads'
    id=Column(Integer,primary_key=True)
    name=Column(String(120),nullable=False)
    contact=Column(String(160),nullable=False)
    service=Column(String(100),nullable=False)
    message=Column(Text,default='')
    status=Column(String(30),default='Novo')
    created=Column(DateTime,default=datetime.utcnow)
Base.metadata.create_all(engine)
app=FastAPI(title='WebCore')
app.add_middleware(SessionMiddleware,secret_key=os.getenv('SESSION_SECRET',secrets.token_urlsafe(48)),same_site='lax',https_only=os.getenv('COOKIE_SECURE','false').lower()=='true')
app.mount('/static',StaticFiles(directory=os.path.join(BASE,'static')),name='static')
t=Jinja2Templates(directory=os.path.join(BASE,'templates'))

def authenticated(r): return r.session.get('auth') is True

def protected(r):
    if not authenticated(r): return RedirectResponse('/portal/login',status_code=303)

def valid_login(user,password):
    u=os.getenv('ADMIN_USER','admin')
    salt=os.getenv('ADMIN_SALT','')
    digest=os.getenv('ADMIN_PASSWORD_HASH','')
    if not salt or not digest: return False
    actual=hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(salt),250000)
    return hmac.compare_digest(user,u) and hmac.compare_digest(actual.hex(),digest)

@app.get('/')
def home(r:Request): return t.TemplateResponse(r,'home.html',{'request':r,'instagram':os.getenv('INSTAGRAM_URL',''),'whatsapp':os.getenv('WHATSAPP_NUMBER',''),'email':os.getenv('CONTACT_EMAIL','')})

@app.post('/orcamento')
def quote(name:str=Form(...),contact:str=Form(...),service:str=Form(...),message:str=Form('')):
    if not (1<=len(name)<=120 and 3<=len(contact)<=160 and len(message)<=3000): raise HTTPException(400,'Dados inválidos')
    with Session() as db:
        db.add(Lead(name=name.strip(),contact=contact.strip(),service=service[:100],message=message.strip()));db.commit()
    return RedirectResponse('/?enviado=1#contato',status_code=303)

@app.get('/portal/login')
def login(r:Request):return t.TemplateResponse(r,'login.html',{'request':r,'error':False})
@app.post('/portal/login')
def login_post(r:Request,user:str=Form(...),password:str=Form(...)):
    if not valid_login(user,password):return t.TemplateResponse(r,'login.html',{'request':r,'error':True},status_code=401)
    r.session.clear();r.session['auth']=True
    return RedirectResponse('/portal',status_code=303)
@app.post('/portal/logout')
def logout(r:Request):r.session.clear();return RedirectResponse('/portal/login',status_code=303)
@app.get('/portal')
def portal(r:Request):
    if x:=protected(r):return x
    return t.TemplateResponse(r,'portal.html',{'request':r})
@app.get('/portal/financeiro')
def finance(r:Request):
    if x:=protected(r):return x
    with Session() as db:
        entries=db.query(Entry).order_by(Entry.created.desc(),Entry.id.desc()).all()
        income=sum((e.amount for e in entries if e.kind=='receita'),Decimal('0'))
        expenses=sum((e.amount for e in entries if e.kind=='despesa'),Decimal('0'))
        return t.TemplateResponse(r,'finance.html',{'request':r,'entries':entries,'income':income,'expenses':expenses,'balance':income-expenses})
@app.post('/portal/financeiro')
def finance_add(r:Request,kind:str=Form(...),description:str=Form(...),category:str=Form(...),amount:str=Form(...)):
    if x:=protected(r):return x
    if kind not in ('receita','despesa') or not description.strip() or len(description)>200 or len(category)>80:raise HTTPException(400)
    try: value=Decimal(amount.replace(',','.'))
    except:raise HTTPException(400,'Valor inválido')
    if value<=0 or value>Decimal('9999999999.99') or not value.is_finite():raise HTTPException(400,'Valor inválido')
    with Session() as db:db.add(Entry(kind=kind,description=description.strip(),category=category.strip(),amount=value));db.commit()
    return RedirectResponse('/portal/financeiro',status_code=303)
@app.post('/portal/financeiro/{entry_id}/excluir')
def finance_delete(r:Request,entry_id:int):
    if x:=protected(r):return x
    with Session() as db:
        e=db.get(Entry,entry_id)
        if e:db.delete(e);db.commit()
    return RedirectResponse('/portal/financeiro',status_code=303)
@app.get('/portal/leads')
def leads(r:Request):
    if x:=protected(r):return x
    with Session() as db:return t.TemplateResponse(r,'leads.html',{'request':r,'leads':db.query(Lead).order_by(Lead.id.desc()).all()})
@app.post('/portal/leads/{lead_id}/status')
def lead_status(r:Request,lead_id:int,status:str=Form(...)):
    if x:=protected(r):return x
    if status not in ('Novo','Em contato','Proposta enviada','Fechado','Perdido'):raise HTTPException(400)
    with Session() as db:
        lead=db.get(Lead,lead_id)
        if lead:lead.status=status;db.commit()
    return RedirectResponse('/portal/leads',status_code=303)
