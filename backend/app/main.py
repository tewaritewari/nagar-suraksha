import os, uuid
from datetime import datetime, timezone
from enum import Enum
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text

DB=os.getenv('DATABASE_URL','postgresql+psycopg://app:app@localhost:5432/nagar_suraksha')
ADMIN_KEY=os.getenv('ADMIN_KEY','change-me')
engine=create_engine(DB, pool_pre_ping=True)
app=FastAPI(title='Nagar Suraksha API', version='0.1.0')

class Category(str,Enum):
    illegal_liquor='illegal_liquor'; suspected_drug='suspected_drug'; public_use='public_use'; distribution='distribution'; other='other'
class Status(str,Enum):
    submitted='submitted'; under_review='under_review'; verified='verified'; rejected='rejected'; action_taken='action_taken'; closed='closed'
class ReportIn(BaseModel):
    category: Category
    description: str = Field(min_length=5,max_length=3000)
    latitude: float = Field(ge=-90,le=90)
    longitude: float = Field(ge=-180,le=180)
    anonymous: bool=True
class StatusIn(BaseModel):
    status: Status
    notes: str|None=None

def init():
    with engine.begin() as c:
      c.execute(text('''CREATE TABLE IF NOT EXISTS reports (id uuid primary key, category varchar(40) not null, description text not null, latitude double precision not null, longitude double precision not null, status varchar(30) not null, anonymous boolean not null default true, created_at timestamptz not null, updated_at timestamptz not null)'''))
      c.execute(text('''CREATE TABLE IF NOT EXISTS actions (id bigserial primary key, report_id uuid references reports(id), status varchar(30) not null, notes text, created_at timestamptz not null)'''))
@app.on_event('startup')
def startup(): init()

def auth(key):
    if key != ADMIN_KEY: raise HTTPException(401,'Authorised dashboard access required')

def public_point(lat,lon):
    # Privacy-preserving grid: ~100m-ish rounding, not exact address disclosure.
    return round(lat,3), round(lon,3)

@app.get('/health')
def health(): return {'ok':True}
@app.post('/reports',status_code=201)
def create_report(r:ReportIn):
    rid=uuid.uuid4(); now=datetime.now(timezone.utc)
    with engine.begin() as c:
      c.execute(text('INSERT INTO reports VALUES (:id,:cat,:desc,:lat,:lon,:status,:anon,:created,:updated)'),dict(id=rid,cat=r.category.value,desc=r.description,lat=r.latitude,lon=r.longitude,status=Status.submitted.value,anon=r.anonymous,created=now,updated=now))
    return {'id':str(rid),'status':Status.submitted.value}
@app.get('/reports/public')
def public_reports():
    with engine.begin() as c:
      rows=c.execute(text("SELECT id,category,status,latitude,longitude,created_at FROM reports WHERE status IN ('under_review','verified','action_taken','closed') ORDER BY created_at DESC LIMIT 1000")).mappings().all()
    return [{**dict(x),'latitude':public_point(x['latitude'],x['longitude'])[0],'longitude':public_point(x['latitude'],x['longitude'])[1]} for x in rows]
@app.get('/reports/admin')
def admin_reports(x_admin_key:str|None=Header(default=None)):
    auth(x_admin_key)
    with engine.begin() as c: return [dict(x) for x in c.execute(text('SELECT * FROM reports ORDER BY created_at DESC LIMIT 2000')).mappings().all()]
@app.patch('/reports/{rid}/status')
def update_status(rid:uuid.UUID, body:StatusIn, x_admin_key:str|None=Header(default=None)):
    auth(x_admin_key); now=datetime.now(timezone.utc)
    with engine.begin() as c:
      res=c.execute(text('UPDATE reports SET status=:s,updated_at=:u WHERE id=:id'),dict(s=body.status.value,u=now,id=rid))
      if res.rowcount==0: raise HTTPException(404,'Report not found')
      c.execute(text('INSERT INTO actions(report_id,status,notes,created_at) VALUES(:id,:s,:n,:t)'),dict(id=rid,s=body.status.value,n=body.notes,t=now))
    return {'id':str(rid),'status':body.status.value}
@app.get('/hotspots')
def hotspots(x_admin_key:str|None=Header(default=None)):
    auth(x_admin_key)
    with engine.begin() as c:
      rows=c.execute(text("SELECT round(latitude::numeric,2) lat, round(longitude::numeric,2) lon, count(*) count FROM reports WHERE status NOT IN ('rejected','closed') GROUP BY 1,2 HAVING count(*) >= 3 ORDER BY count DESC LIMIT 100")).mappings().all()
    return [dict(x) for x in rows]
