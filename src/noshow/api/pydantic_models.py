from datetime import date, datetime

from pydantic import BaseModel


class Appointment(BaseModel):
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
    status: str
    status_code_original: str | None
    cancelationReason_code: str | None
    cancelationReason_display: str | None
    BIRTH_YEAR: int
    address_postalCodeNumbersNL: int
    name: str | None
    description: str | None
    name_text: str | None
    name_given1_callMe: str | None
    telecom1_value: str | None
    telecom2_value: str | None
    telecom3_value: str | None
    birthDate: date
