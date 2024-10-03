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
    cancelationReason_code: str | None
    cancelationReason_display: str | None
    BIRTH_YEAR: int
    address_postalCodeNumbersNL: int
    name: str | None
    description: str | None
    name_text: str | None
    patient_id: str | None
    name_given1_callMe: str | None
    telecom1_value: str | None
    telecom2_value: str | None
    telecom3_value: str | None
    birthDate: date

    @field_validator("birthDate", mode="before")
    def convert_milliseconds_to_datetime(cls, value):
        """birthDate is always returned as ms, not seconds so change validator"""
        if isinstance(value, (str, int, float)):
            return date.fromtimestamp(float(value) / 1000)
        return value
