from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List
import bcrypt
import os
from dotenv import load_dotenv

from database import get_db, engine
import models, schemas

load_dotenv()
models.Base.metadata.create_all(bind=engine)

SECRET_KEY         = os.getenv("SECRET_KEY", "agroship-secret-key-2025")
ALGORITHM          = "HS256"
TOKEN_EXPIRE_HOURS = 12

oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

app = FastAPI(title="AgroShip India API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_password(plain: str, hashed: str) -> bool:
    try:
        plain_bytes  = plain.encode("utf-8")
        hashed_bytes = hashed.encode("utf-8")
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except Exception as e:
        print(f"[verify_password ERROR] {e}")
        return False

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")

def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)):
    exc = HTTPException(status_code=401, detail="Invalid or expired token",
                        headers={"WWW-Authenticate": "Bearer"})
    try:
        payload  = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        if user_id is None:
            raise exc
    except JWTError:
        raise exc
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or not user.is_active:
        raise exc
    return user

@app.get("/")
def root():
    return {"message": "AgroShip India API running"}

# ── AUTH ──────────────────────────────────────────────────────
@app.post("/api/auth/login", response_model=schemas.Token)
def login(body: schemas.LoginRequest, db: Session = Depends(get_db)):
    print(f"[LOGIN ATTEMPT] email={body.email}")
    user = db.query(models.User).filter(models.User.email == body.email).first()
    if not user:
        print("[LOGIN] No user found with that email")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    print(f"[LOGIN] User found. Hash={user.password[:20]}...")
    ok = verify_password(body.password, user.password)
    print(f"[LOGIN] Password match = {ok}")
    if not ok:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer",
            "user_name": user.name, "role": user.role}

@app.post("/api/auth/reset-password")
def reset_password(db: Session = Depends(get_db)):
    """Emergency endpoint — sets admin password to admin123"""
    user = db.query(models.User).filter(models.User.email == "admin@agroshipindia.com").first()
    if not user:
        user = models.User(name="Admin", email="admin@agroshipindia.com", role="admin", is_active=True)
        db.add(user)
    user.password = hash_password("admin123")
    db.commit()
    return {"message": "Password reset to admin123 successfully"}

# ── PRODUCTS ──────────────────────────────────────────────────
@app.get("/api/products", response_model=List[schemas.ProductOut])
def list_products(status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(models.Product)
    if status:
        q = q.filter(models.Product.status == status)
    return q.order_by(models.Product.created_at.desc()).all()

@app.get("/api/products/{pid}", response_model=schemas.ProductOut)
def get_product(pid: int, db: Session = Depends(get_db)):
    p = db.query(models.Product).filter(models.Product.id == pid).first()
    if not p:
        raise HTTPException(404, "Product not found")
    return p

@app.post("/api/products", response_model=schemas.ProductOut, status_code=201)
def create_product(body: schemas.ProductCreate, db: Session = Depends(get_db),
                   _=Depends(get_current_user)):
    p = models.Product(**body.model_dump())
    db.add(p); db.commit(); db.refresh(p)
    return p

@app.put("/api/products/{pid}", response_model=schemas.ProductOut)
def update_product(pid: int, body: schemas.ProductUpdate, db: Session = Depends(get_db),
                   _=Depends(get_current_user)):
    p = db.query(models.Product).filter(models.Product.id == pid).first()
    if not p:
        raise HTTPException(404, "Product not found")
    for k, v in body.model_dump().items():
        setattr(p, k, v)
    db.commit(); db.refresh(p)
    return p

@app.delete("/api/products/{pid}")
def delete_product(pid: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    p = db.query(models.Product).filter(models.Product.id == pid).first()
    if not p:
        raise HTTPException(404, "Product not found")
    db.delete(p); db.commit()
    return {"message": "Product deleted"}

# ── ORDERS ────────────────────────────────────────────────────
@app.post("/api/orders", response_model=schemas.OrderOut, status_code=201)
def place_order(body: schemas.OrderCreate, db: Session = Depends(get_db)):
    order = models.Order(**body.model_dump())
    db.add(order); db.commit(); db.refresh(order)
    return order

@app.get("/api/orders", response_model=List[schemas.OrderOut])
def list_orders(status: Optional[str] = None, db: Session = Depends(get_db),
                _=Depends(get_current_user)):
    q = db.query(models.Order)
    if status:
        q = q.filter(models.Order.status == status)
    return q.order_by(models.Order.created_at.desc()).all()

@app.patch("/api/orders/{oid}/status", response_model=schemas.OrderOut)
def update_order_status(oid: int, body: schemas.OrderStatusUpdate,
                        db: Session = Depends(get_db), _=Depends(get_current_user)):
    o = db.query(models.Order).filter(models.Order.id == oid).first()
    if not o:
        raise HTTPException(404, "Order not found")
    o.status = body.status
    db.commit(); db.refresh(o)
    return o

@app.delete("/api/orders/{oid}")
def delete_order(oid: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    o = db.query(models.Order).filter(models.Order.id == oid).first()
    if not o:
        raise HTTPException(404, "Order not found")
    db.delete(o); db.commit()
    return {"message": "Order deleted"}

# ── INQUIRIES ─────────────────────────────────────────────────
@app.post("/api/inquiries", response_model=schemas.InquiryOut, status_code=201)
def submit_inquiry(body: schemas.InquiryCreate, db: Session = Depends(get_db)):
    inq = models.Inquiry(**body.model_dump())
    db.add(inq); db.commit(); db.refresh(inq)
    return inq

@app.get("/api/inquiries", response_model=List[schemas.InquiryOut])
def list_inquiries(status: Optional[str] = None, db: Session = Depends(get_db),
                   _=Depends(get_current_user)):
    q = db.query(models.Inquiry)
    if status:
        q = q.filter(models.Inquiry.status == status)
    return q.order_by(models.Inquiry.created_at.desc()).all()

@app.patch("/api/inquiries/{iid}/status", response_model=schemas.InquiryOut)
def update_inquiry_status(iid: int, body: schemas.InquiryStatusUpdate,
                          db: Session = Depends(get_db), _=Depends(get_current_user)):
    inq = db.query(models.Inquiry).filter(models.Inquiry.id == iid).first()
    if not inq:
        raise HTTPException(404, "Inquiry not found")
    inq.status = body.status
    db.commit(); db.refresh(inq)
    return inq

@app.delete("/api/inquiries/{iid}")
def delete_inquiry(iid: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    inq = db.query(models.Inquiry).filter(models.Inquiry.id == iid).first()
    if not inq:
        raise HTTPException(404, "Inquiry not found")
    db.delete(inq); db.commit()
    return {"message": "Inquiry deleted"}

# ── SETTINGS ──────────────────────────────────────────────────
@app.get("/api/settings", response_model=schemas.SettingsOut)
def get_settings(db: Session = Depends(get_db)):
    rows = db.query(models.Setting).all()
    return {r.setting_key: r.value for r in rows}

@app.put("/api/settings")
def update_settings(body: schemas.SettingUpdate, db: Session = Depends(get_db),
                    _=Depends(get_current_user)):
    for key, val in body.model_dump(exclude_none=True).items():
        row = db.query(models.Setting).filter(models.Setting.setting_key == key).first()
        if row:
            row.value = val
        else:
            db.add(models.Setting(setting_key=key, value=val))
    db.commit()
    return {"message": "Settings updated"}

# ── DASHBOARD ─────────────────────────────────────────────────
@app.get("/api/dashboard", response_model=schemas.DashboardStats)
def dashboard(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return {
        "total_products":  db.query(models.Product).count(),
        "active_products": db.query(models.Product).filter(models.Product.status == "active").count(),
        "total_orders":    db.query(models.Order).count(),
        "new_orders":      db.query(models.Order).filter(models.Order.status == "NEW").count(),
        "total_inquiries": db.query(models.Inquiry).count(),
        "new_inquiries":   db.query(models.Inquiry).filter(models.Inquiry.status == "NEW").count(),
    }