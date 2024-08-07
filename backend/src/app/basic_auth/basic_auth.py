from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import schemas
from passlib.context import CryptContext

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


@app.post("/register/", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/login/")
def login(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == credentials.username).first()
    if db_user is None or not verify_password(credentials.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return {"message": "Login successful"}


@app.get("/protected/")
def read_protected(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == credentials.username).first()
    if db_user is None or not verify_password(credentials.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return {"message": "This is a protected endpoint"}
