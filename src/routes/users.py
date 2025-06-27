from slowapi import Limiter
from fastapi import Request, APIRouter, Depends, UploadFile, HTTPException, status, File
from slowapi.util import get_remote_address
from src.auth.auth import get_current_user
from src.databases.connect import get_db
from src.databases.models import User
from src.schemas.user import UserOut
from src.services.update_avatar import upload_avatar

router = APIRouter(prefix="/users", tags=["users"])

limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/me",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    description="No more than 10 requests per minute",
)
@limiter.limit("5/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """
    Получить информацию о текущем аутентифицированном пользователе.

    Ограничение: не более 5 запросов в минуту.

    Args:
        request (Request): HTTP запрос.
        user (User): Текущий пользователь, полученный через Depends.

    Returns:
        UserOut: Модель с информацией о пользователе.
    """
    return user


@router.post(
    "/avatar", description="Update user avatar", status_code=status.HTTP_201_CREATED
)
async def update_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Обновить аватар текущего пользователя.

    Принимает файл изображения, проверяет его тип,
    загружает на внешний сервис (upload_avatar),
    обновляет URL аватара в базе данных и возвращает новый URL.

    Args:
        file (UploadFile): Загружаемый файл (требуется быть изображением).
        current_user (User): Текущий пользователь из Depends.
        db (Session): Сессия базы данных из Depends.

    Raises:
        HTTPException: если файл не является изображением.

    Returns:
        dict: Словарь с ключом "avatar_url" и значением - URL загруженного аватара.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Файл має бути зображенням"
        )

    public_id = f"user_avatars/{current_user.id}"
    avatar_url = upload_avatar(file, public_id)

    current_user.avatar = avatar_url
    db.commit()
    db.refresh(current_user)

    return {"avatar_url": avatar_url}
