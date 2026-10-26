from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from collections import deque
import json
import os

app = FastAPI(title="Flantech Local Database API Gateway")
DB_FILE = "flantech_members.json"
RANK_BONUS_RATES = {"Bronze": 0.25, "Silver": 0.30, "Gold": 0.35, "Diamond": 0.40}

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {
        "60123456789": {
            "name": "Admin Leader", "password": "admin", "sponsor": None,
            "upline": None, "children": [], "rank": "Diamond", "wallet": 0.0, "team_sales_cv": 0.0
        }
    }

def save_db(db):
    with open(DB_FILE, "w") as f: json.dump(db, f, indent=4)

class RegisterModel(BaseModel):
    name: str
    phone: str
    password: str
    sponsor: str
    pkg_cv: float

class SaleModel(BaseModel):
    buyer_phone: str
    cv_amount: float

@app.get("/members")
def get_all_members():
    # Safely strips passwords before transmitting logs to the public cloud dashboard
    db = load_db()
    clean_db = {}
    for phone, info in db.items():
        clean_db[phone] = {k: v for k, v in info.items() if k != "password"}
    return clean_db

@app.post("/login")
def login(payload: dict):
    db = load_db()
    phone = payload.get("phone")
    password = payload.get("password")
    if phone in db and db[phone]["password"] == password:
        return {"status": "success", "member": db[phone]}
    raise HTTPException(status_code=401, detail="Unauthorized credentials")

@app.post("/register")
def register(member: RegisterModel):
    db = load_db()
    if member.phone in db: raise HTTPException(status_code=400, detail="Phone already registered")
    if member.sponsor not in db: raise HTTPException(status_code=400, detail="Sponsor not found")
    
    # 3MP Placement Logic running securely inside local system memory
    queue = deque([member.sponsor])
    assigned_upline = member.sponsor
    while queue:
        curr = queue.popleft()
        if len(db[curr]["children"]) < 3:
            assigned_upline = curr
            break
        queue.extend(db[curr]["children"])
        
    def determine_rank(cv):
        if cv >= 1000: return "Diamond"
        elif cv >= 500: return "Gold"
        elif cv >= 300: return "Silver"
        elif cv >= 100: return "Bronze"
        return "Member"
        
    db[member.phone] = {
        "name": member.name, "password": member.password, "sponsor": member.sponsor,
        "upline": assigned_upline, "children": [], "rank": determine_rank(member.pkg_cv),
        "wallet": 0.0, "team_sales_cv": 0.0
    }
    db[assigned_upline]["children"].append(member.phone)
    save_db(db)
    return {"status": "success"}

@app.post("/sale")
def sale(tx: SaleModel):
    db = load_db()
    if tx.buyer_phone not in db: raise HTTPException(status_code=404, detail="Member not found")
    
    sponsor_phone = db[tx.buyer_phone]["sponsor"]
    if sponsor_phone in db:
        rate = RANK_BONUS_RATES.get(db[sponsor_phone]["rank"], 0.25)
        db[sponsor_phone]["wallet"] += round(tx.cv_amount * rate, 2)
        
    curr_upline = db[tx.buyer_phone]["upline"]
    while curr_upline:
        if curr_upline in db:
            db[curr_upline]["team_sales_cv"] += tx.cv_amount
            curr_upline = db[curr_upline]["upline"]
        else: break
        
    save_db(db)
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
