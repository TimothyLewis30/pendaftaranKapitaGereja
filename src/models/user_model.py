from pydantic import BaseModel, Field


class RegistrationCreate(BaseModel):
    full_name:          str = Field(..., min_length=3, max_length=100, example="Budi Santoso")
    email:              str = Field(..., example="budi@email.com")
    phone:              str = Field(..., min_length=8, max_length=20, example="08123456789")
    church_gkode:       str = Field(..., min_length=1, max_length=10, example="GKY001")
    kapita_id_sesi_1:   int = Field(..., gt=0, example=1)
    kapita_id_sesi_2:   int = Field(..., gt=0, example=2)


class RegistrationResponse(BaseModel):
    id:                 int
    full_name:          str
    email:              str
    phone:              str
    church_gkode:       str
    church_name:        str
    kapita_id_sesi_1:   int
    kapita_name_sesi_1: str
    kapita_id_sesi_2:   int
    kapita_name_sesi_2: str
    registered_at:      str


class RegistrationCheckResponse(BaseModel):
    email:       str
    is_registered: bool
    message:     str


class UserCreate(BaseModel):
    full_name:          str = Field(..., min_length=3, max_length=100, example="Budi Santoso")
    email:              str = Field(..., example="budi@email.com")
    phone:              str = Field(..., min_length=8, max_length=20, example="08123456789")
    church_gkode:       str = Field(..., min_length=1, max_length=10, example="GKY001")
    ukapita_sesi_1:     int = Field(..., gt=0, example=1)
    ukapita_sesi_2:     int = Field(..., gt=0, example=2)


class UserResponse(BaseModel):
    uid:              int
    full_name:        str
    email:            str
    phone:            str
    church_gkode:     str
    church_name:      str
    ukapita_sesi_1:   int
    kapita_name_sesi_1: str
    ukapita_sesi_2:   int
    kapita_name_sesi_2: str
    registered_at:    str
