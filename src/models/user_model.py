from pydantic import BaseModel, Field
from typing import Optional


class RegistrationCreate(BaseModel):
    full_name:      str = Field(..., min_length=3, max_length=100, example="Budi Santoso")
    email:          str = Field(..., example="budi@email.com")
    phone:          str = Field(..., min_length=8, max_length=20, example="08123456789")
    birth_date:     str = Field(..., example="1995-08-17", description="Format: YYYY-MM-DD")
    address:        str = Field(..., min_length=5, example="Jl. Merdeka No. 1, Jakarta")
    church_gkode:   str = Field(..., min_length=1, max_length=10, example="GKY001")
    kapita_id:      int = Field(..., gt=0, example=1)
    notes:          Optional[str] = Field(None, example="Saya tertarik bergabung di pelayanan musik")


class RegistrationResponse(BaseModel):
    id:             int
    full_name:      str
    email:          str
    phone:          str
    birth_date:     str
    address:        str
    church_gkode:   str
    church_name:    str
    kapita_id:      int
    kapita_name:    str
    notes:          Optional[str]
    registered_at:  str


class RegistrationCheckResponse(BaseModel):
    email:       str
    is_registered: bool
    message:     str


class UserCreate(BaseModel):
    full_name:      str = Field(..., min_length=3, max_length=100, example="Budi Santoso")
    email:          str = Field(..., example="budi@email.com")
    phone:          str = Field(..., min_length=8, max_length=20, example="08123456789")
    birth_date:     str = Field(..., example="1995-08-17", description="Format: YYYY-MM-DD")
    address:        str = Field(..., min_length=5, example="Jl. Merdeka No. 1, Jakarta")
    church_gkode:   str = Field(..., min_length=1, max_length=10, example="GKY001")
    ukapita:        int = Field(..., gt=0, example=1)
    notes:          Optional[str] = Field(None, example="Saya tertarik bergabung di pelayanan musik")


class UserResponse(BaseModel):
    uid:          int
    full_name:    str
    email:        str
    phone:        str
    birth_date:   str
    address:      str
    church_gkode: str
    church_name:  str
    ukapita:      int
    kapita_name:  str
    notes:        Optional[str]
    registered_at: str
