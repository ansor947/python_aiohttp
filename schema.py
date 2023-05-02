from typing import Optional
import pydantic


class CreateAdvertisements(pydantic.BaseModel):
    header: str
    description: str
    owner: str

    @pydantic.validator("header")
    async def min_max_length(cls, value: str):
        if 1 > len(value) > 30:
            raise ValueError('Header too short')
        return value


class PatchAdvertisements(pydantic.BaseModel):
    header: Optional[str]
    description: Optional[str]
    owner: Optional[str]
