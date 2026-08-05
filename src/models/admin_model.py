from pydantic import BaseModel, Field
from typing import Optional


class AdminCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email:    str = Field(...)
    password: str = Field(..., min_length=6)
    role:     Optional[str] = Field(None, description="Role: 'Admin', 'SuperAdmin', atau 'NULL' untuk set NULL")


class AdminUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    email:    Optional[str] = Field(None)
    password: Optional[str] = Field(None, min_length=6)
    role:     Optional[str] = Field(None, description="Role: 'Admin', 'SuperAdmin', atau 'NULL' untuk set NULL")


class AdminLogin(BaseModel):
    email:    str = Field(...)
    password: str = Field(...)


class AdminResponse(BaseModel):
    aid:      int
    username: str
    email:    str
    role:     Optional[str]
