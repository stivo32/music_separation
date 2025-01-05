from pydantic import EmailStr
from jose import jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fourier.auth.schemas import EmailModel
from fourier.auth.utils import verify_password
from fourier.config import settings
from fourier.auth.dao import UsersDAO
from fourier.dao.session_maker import SessionDep


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=30)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encode_jwt


async def authenticate_user(email: EmailStr, password: str, session: AsyncSession = SessionDep):
    user = await UsersDAO.find_one_or_none(session=session, filters=EmailModel(email=email))
    if not user or not verify_password(plain_password=password, hashed_password=user.password):
        return None
    return user
