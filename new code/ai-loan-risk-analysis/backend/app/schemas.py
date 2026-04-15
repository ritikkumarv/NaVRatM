from pydantic import BaseModel, Field, field_validator


class VerifyUserRequest(BaseModel):
    pan: str = Field(
        ...,
        min_length=10,
        max_length=10,
        description="PAN number",
        examples=["ABCDE1234F"],
    )
    aadhaar: str = Field(
        ...,
        min_length=12,
        max_length=14,
        description="12-digit Aadhaar number",
        examples=["123412341234"],
    )

    @field_validator("pan", mode="before")
    @classmethod
    def normalize_pan(cls, value: str) -> str:
        return str(value).strip().upper()

    @field_validator("aadhaar", mode="before")
    @classmethod
    def normalize_aadhaar(cls, value: str) -> str:
        digits = "".join(ch for ch in str(value) if ch.isdigit())
        if len(digits) != 12:
            raise ValueError("Aadhaar must contain exactly 12 digits.")
        return digits


class VerifyUserResponse(BaseModel):
    pan: str
    pan_verified: bool
    aadhaar: str
    aadhaar_verified: bool
    itr_pan: str
    itr_status: str
    blacklist_pan: str
    is_blacklisted: bool
