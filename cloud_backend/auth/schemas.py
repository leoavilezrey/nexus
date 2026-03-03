from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class User(BaseModel):
    email: EmailStr
    is_active: bool = True

class UserInDB(User):
    hashed_password: str
