from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from database import engine, SessionLocal
import models
from auth import hash_password, verify_password
app = FastAPI()

models.Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"status": "Server is running"}

@app.post("/users")
def create_user(name: str, email: str, password: str):
    db = SessionLocal()
    user = models.User(
        name=name,
        email=email,
        password_hash=hash_password(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return {"id": user.id, "email": user.email}

@app.get("/users")
def get_users():
    db = SessionLocal()
    users = db.query(models.User).all()
    db.close()
    return users

@app.post("/login")
def login(email: str, password: str):
    db = SessionLocal()
    user = db.query(models.User).filter(models.User.email == email).first()
    db.close()
    if not user or not verify_password(password, user.password_hash):
        return {"error": "Invalid credentials. Try again"}

    return {"message": "Login successful"}

@app.put("/users/{user_id}")
def update_user(user_id: int, name: str):
    db = SessionLocal()
    user = db.query(models.User).get(user_id)

    if not user:
        db.close()
        return {"error": "User not found"}
    user.name = name
    db.commit()
    db.close()
    return {"message": "Updated"}

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    db = SessionLocal()
    user = db.query(models.User).get(user_id)
    if not user:
        db.close()
        return {"error": "User not found"}
    db.delete(user)
    db.commit()
    db.close()
    return {"message": "Deleted"}

templates = Jinja2Templates(directory="templates")

@app.get("/page")
def page(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )
