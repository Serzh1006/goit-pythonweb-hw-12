from src.schemas.user import UserCreate, UserLogin
from src.databases.connect import get_db
from fastapi import Depends, HTTPException, APIRouter, status, BackgroundTasks, Request
from src.databases.models import User
from src.repository.users import create_user, authenticate_user
from src.auth.auth import create_access_token
from src.services.email_token import decode_email_token
from src.services.email import send_verification_email



router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/verify-email/{token}")
async def verify_email(token: str, db = Depends(get_db)):
    email = await decode_email_token(token)
    if email is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.confirmed = True
    db.commit()
    return {"message": "Email successfully verified!"}


@router.post("/signup", status_code = status.HTTP_201_CREATED)
async def register(user: UserCreate, background_tasks: BackgroundTasks, request: Request, db = Depends(get_db)):
    existing = db.query(User).filter_by(email=user.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    new_user = await create_user(user, db)
    background_tasks.add_task(send_verification_email, new_user.email, new_user.username, str(request.base_url))
    return {"Email": new_user.email}


@router.post("/login", status_code = status.HTTP_201_CREATED)
async def login(user: UserLogin, db = Depends(get_db)):
    user_in_db = await authenticate_user(user.email, user.password, db)
    if not user_in_db:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED ,detail="Invalid authorization")
    token = await create_access_token({"sub": user_in_db.email})
    return {"access_token": token, "token_type": "bearer"}