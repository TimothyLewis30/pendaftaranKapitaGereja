from pydantic import BaseModel, Field
from typing import Optional


class RegistrationCreate(BaseModel):
    uparticipant:       int = Field(..., gt=0)
    kapita_id_sesi_1:   int = Field(..., gt=0)
    kapita_id_sesi_2:   int = Field(..., gt=0)


class RegistrationResponse(BaseModel):
    id:                 int
    full_name:          str
    church_gkode:       str
    church_name:        str
    kapita_id_sesi_1:   int
    kapita_name_sesi_1: str
    kapita_id_sesi_2:   int
    kapita_name_sesi_2: str
    uparticipant:       Optional[int]
    registered_at:      str


class UserCreate(BaseModel):
    uparticipant:       int = Field(..., gt=0)
    ukapita_sesi_1:     int = Field(..., gt=0)
    ukapita_sesi_2:     int = Field(..., gt=0)


class UserResponse(BaseModel):
    uid:                int
    full_name:          str
    church_gkode:       str
    church_name:        str
    ukapita_sesi_1:     int
    kapita_name_sesi_1: str
    ukapita_sesi_2:     int
    kapita_name_sesi_2: str
    uparticipant:       Optional[int]
    registered_at:      str


class CetakExcelRequest(BaseModel):
    pilihan: int = Field(..., ge=1, le=4)
    sesi_1: Optional[int] = Field(None)
    sesi_2: Optional[int] = Field(None)
    gkode: Optional[str] = Field(None)

