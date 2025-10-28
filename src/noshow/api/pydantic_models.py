from datetime import date, datetime

from pydantic import BaseModel, field_validator


class Appointment(BaseModel):
    """Pydantic model for appointment data, used by the FastAPI predict endpoint"""

    APP_ID: str
    pseudo_id: str
    hoofdagenda: str
    hoofdagenda_id: str
    subagenda_id: str
    specialty_code: str | None
    soort_consult: str | None
    afspraak_code: str
    start: datetime
    end: datetime
    gearriveerd: datetime | None
    created: datetime
    minutesDuration: int
    status: str | None
    status_code_original: str | None
    mutationReason_code: str | None
    mutationReason_display: str | None
    BIRTH_YEAR: int
    address_postalCodeNumbersNL: int | None
    name: str | None
    description: str | None
    name_text: str | None
    patient_id: str | None
    name_given1_callMe: str | None
    telecom1_value: str | None
    telecom2_value: str | None
    telecom3_value: str | None
    birthDate: datetime

    @field_validator("birthDate", mode="before")
    def convert_milliseconds_to_datetime(cls, value):
        """birthDate is always returned as ms, not seconds so change validator"""
        if (
            isinstance(value, str)
            and value.replace(".", "").replace("-", "").isnumeric()
        ):
            return date.fromtimestamp(float(value) / 1000)
        if isinstance(value, (int, float)):
            return date.fromtimestamp(float(value) / 1000)
        # If value is already a string in the correct format, return it
        return value

    @field_validator("address_postalCodeNumbersNL", mode="before")
    def convert_empty_postal_code(cls, value):
        """Postalcodes are sometimes empty, convert them to None"""
        if value == "":
            return None
        return value
