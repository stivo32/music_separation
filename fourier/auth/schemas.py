from pydantic import BaseModel, ConfigDict, EmailStr, Field, validator
from fourier.auth.utils import get_password_hash


class EmailModel(BaseModel):
    email: EmailStr = Field(description="Email")
    model_config = ConfigDict(from_attributes=True)


class SUserRegister(EmailModel):
    password: str = Field(min_length=5, max_length=50, description="Password, from 5 to 50 symbols")
    confirm_password: str = Field(min_length=5, max_length=50, description="Repeat password")

    @validator("confirm_password", pre=False, always=True)
    def check_password(cls, confirm_password, values):
        password = values.get("password")
        if password != confirm_password:
            raise ValueError("Passwords are not the same")
        values["password"] = get_password_hash(password)
        return confirm_password


class SUserAddDB(EmailModel):
    password: str = Field(min_length=5, description="Password in hash format")


class SUserAuth(EmailModel):
    password: str = Field(min_length=5, max_length=50, description="Password, from 5 to 50 symbols")


class RoleModel(BaseModel):
    id: int = Field(description="Role id")
    name: str = Field(description="Role name")
    model_config = ConfigDict(from_attributes=True)


class SUserInfo(EmailModel):
    id: int = Field(description="User id")
    role: RoleModel = Field(exclude=True)

    @property
    def role_name(self) -> str:
        return self.role.name

    @property
    def role_id(self) -> int:
        return self.role.id
