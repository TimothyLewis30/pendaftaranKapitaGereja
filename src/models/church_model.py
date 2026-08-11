from pydantic import BaseModel, Field
from typing import Optional, List


class ChurchCreate(BaseModel):
    name:  str = Field(..., min_length=1, max_length=255)


class ChurchUpdate(BaseModel):
    name:  str = Field(..., min_length=1, max_length=255)


class ChurchResponse(BaseModel):
    id:         str
    name:       str
    kapita:     List[dict]


class ChurchQuotaResponse(BaseModel):
    church_gkode:   str
    church_name:    str
    kapita_quotas:  List[dict]


class ChurchKapitaQuotaCreate(BaseModel):
    kapita_id:  int = Field(..., gt=0)
    kuota_sesi_1: int = Field(..., ge=0)
    kuota_sesi_2: int = Field(..., ge=0)


class ChurchKapitaQuotaResponse(BaseModel):
    gkid:       int
    gkode:      str
    idkapita:   int
    kapita_name: str
    kuota:      int
