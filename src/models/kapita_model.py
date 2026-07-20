from pydantic import BaseModel, Field
from typing import Optional


class KapitaCreate(BaseModel):
    namakapita: str = Field(..., min_length=1, max_length=20, example="Kapita 1")


class KapitaResponse(BaseModel):
    idkapita:    int
    namakapita:  str
