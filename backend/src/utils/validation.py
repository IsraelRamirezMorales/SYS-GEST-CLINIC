from typing import Annotated, Literal

from pydantic import Field, StringConstraints

SesionType = Literal["Consulta", "Terapia", "Alberca"]

Id = Annotated[int, Field(gt=0)]
PersonName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Phone = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=25)]
ShortText = Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)]
LongText = Annotated[str, StringConstraints(max_length=20000)]
Amount = Annotated[int, Field(ge=0, le=10_000_000)]
