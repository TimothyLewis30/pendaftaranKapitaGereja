from pydantic import BaseModel, Field
from typing import Optional, List


class ChurchCreate(BaseModel):
    name:  str = Field(..., min_length=1, max_length=255, example="GKPI Resort Menteng")


class ChurchUpdate(BaseModel):
    name:  str = Field(..., min_length=1, max_length=255, example="GKPI Resort Menteng")


class ChurchResponse(BaseModel):
    id:         str
    name:       str
    kapita:     List[dict]


class ChurchQuotaResponse(BaseModel):
    church_gkode:   str
    church_name:    str
    kapita_quotas:  List[dict]


class ChurchKapitaQuotaCreate(BaseModel):
    kapita_id:  int = Field(..., gt=0, example=1)
    kuota:      int = Field(..., ge=0, example=10)


class ChurchKapitaQuotaResponse(BaseModel):
    gkid:       int
    gkode:      str
    idkapita:   int
    kapita_name: str
    kuota:      int
