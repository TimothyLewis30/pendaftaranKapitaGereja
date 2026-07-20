from pydantic import BaseModel, Field
from typing import Optional


class AdminCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=100, example="admin01")
    email:    str = Field(..., example="admin01@gereja.com")
    password: str = Field(..., min_length=6, example="password123")
    role:     Optional[str] = Field(None, example="Admin", description="Role: 'Admin', 'SuperAdmin', atau 'NULL' untuk set NULL")


class AdminUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=100, example="admin01")
    email:    Optional[str] = Field(None, example="admin01@gereja.com")
    password: Optional[str] = Field(None, min_length=6, example="password123")
    role:     Optional[str] = Field(None, example="Admin", description="Role: 'Admin', 'SuperAdmin', atau 'NULL' untuk set NULL")


class AdminLogin(BaseModel):
    email:    str = Field(..., example="admin01@gereja.com")
    password: str = Field(..., example="password123")


class AdminResponse(BaseModel):
    aid:      int
    username: str
    email:    str
    role:     Optional[str]
