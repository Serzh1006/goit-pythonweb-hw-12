from src.schemas.user import UserCreate, UserLogin
from src.databases.connect import get_db
from sqlalchemy import select
from fastapi import (
    Depends,
    HTTPException,
    APIRouter,
    status,
    BackgroundTasks,
    Request,
    Form,
)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.databases.models import User
from src.repository.users import create_user, authenticate_user
from src.auth.auth import (
    create_access_token,
    create_password_reset_token,
    verify_password_reset_token,
    Hash,
)
from src.services.email_token import decode_email_token
from src.services.email import send_verification_email, send_reset_email

hasher = Hash()

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="src/templates")


@router.get("/new-password/{token}", response_class=HTMLResponse)
async def reset_password_form(request: Request, token: str):
    return templates.TemplateResponse(
        "reset_form.html", {"request": request, "token": token}
    )


@router.post("/reset-password")
async def reset_password(
    token: str = Form(...), new_password: str = Form(...), db=Depends(get_db)
):
    """
    Скидає пароль користувача на новий, використовуючи токен скидання пароля.

    Args:
        token (str): JWT-токен для скидання пароля, надісланий на email.
        new_password (str): Новий пароль, який потрібно встановити.
        db (Session): Сесія бази даних.

    Raises:
        HTTPException: Якщо токен недійсний або користувача не знайдено.

    Returns:
        dict: Повідомлення про успішне оновлення пароля.
    """
    email = await verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = hasher.get_password_hash(new_password)
    db.commit()
    return {"message": "Password updated successfully"}


@router.post("/request-password-reset")
async def request_password_reset(
    email: str, background_tasks: BackgroundTasks, request: Request, db=Depends(get_db)
):
    """
    Надсилає листа з посиланням на скидання пароля користувачу на email.

    Args:
        email (str): Email-адреса користувача, який хоче скинути пароль.
        background_tasks (BackgroundTasks): Об'єкт для фонової відправки email.
        request (Request): HTTP-запит, використовується для отримання базової URL-адреси.
        db (Session): Сесія бази даних.

    Raises:
        HTTPException: Якщо користувача з таким email не знайдено.

    Returns:
        dict: Повідомлення про відправлення посилання для скидання пароля.
    """
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    background_tasks.add_task(
        send_reset_email, user.email, user.username, str(request.base_url)
    )
    return {"message": "Reset link sent"}


@router.get("/verify-email/{token}")
async def verify_email(token: str, db=Depends(get_db)):
    """
    Підтверджує електронну пошту користувача за допомогою токена верифікації.

    - **token**: токен підтвердження, який користувач отримав на email
    - Після успішної перевірки встановлює `confirmed=True` у базі даних

    Raises:
        - 400: якщо токен невалідний або протермінований
        - 404: якщо користувача не знайдено
    """
    email = await decode_email_token(token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
        )
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    user.confirmed = True
    db.commit()
    return {"message": "Email successfully verified!"}


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def register(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db=Depends(get_db),
):
    """
    Реєструє нового користувача та надсилає йому листа для верифікації email.

    - **user**: дані користувача для реєстрації (username, email, password)
    - **request**: потрібен для побудови базового URL у листі
    - **background_tasks**: використовується для надсилання email асинхронно

    Raises:
        - 409: якщо email вже зареєстрований

    Returns:
        - email користувача у відповідь
    """
    result = await db.execute(select(User).where(User.email == user.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )
    new_user = await create_user(user, db)
    background_tasks.add_task(
        send_verification_email,
        new_user.email,
        new_user.username,
        str(request.base_url),
    )
    return {"Email": new_user.email}


@router.post("/login", status_code=status.HTTP_201_CREATED)
async def login(user: UserLogin, db=Depends(get_db)):
    """
    Авторизує користувача та повертає JWT токен доступу.

    - **user**: email і пароль
    - Повертає токен, якщо авторизація успішна

    Raises:
        - 401: якщо email або пароль неправильні

    Returns:
        - access_token (JWT)
        - token_type (Bearer)
    """
    user_in_db = await authenticate_user(user.email, user.password, db)
    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization"
        )
    token = await create_access_token({"sub": user_in_db.email})
    return {"access_token": token, "token_type": "bearer"}
