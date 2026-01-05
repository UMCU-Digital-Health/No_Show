from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase, MappedAsDataclass):
    """Base declarative class for SQLAlchemy models in the noshow schema.

    This class configures the declarative base and enables dataclass-like
    behavior (MappedAsDataclass) for ORM model classes defined in this module.
    All ORM models should inherit from this Base so they share the same
    metadata and dataclass mapping behavior.
    """

    pass


class ApiRequest(Base):
    """ORM model for an API request recorded in the noshow.apirequest table.

    Attributes
    ----------
    id : int
        Primary key for the request record.
    timestamp : datetime
        Time the request was made.
    response_code : int
        HTTP or service response code returned for the request.
    response_message : str
        Message or body returned with the response.
    endpoint : str
        API endpoint that was called.
    runtime : float
        Execution/runtime of the request in seconds.
    api_version : str
        Version of the API used for the request.
    """

    __tablename__ = "apirequest"
    __table_args__ = {"schema": "noshow"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, init=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime)
    response_code: Mapped[int] = mapped_column(Integer, index=True)
    response_message: Mapped[str]
    endpoint: Mapped[str]
    runtime: Mapped[float]
    api_version: Mapped[str]


class ApiPatient(Base):
    """ORM model for a patient referenced by the API stored in noshow.apipatient.

    Attributes
    ----------
    id : str
        Primary key patient identifier (up to 64 characters).
    call_number : int | None
        Optional call attempt number for the patient.
    opt_out : int | None
        Optional flag indicating whether the patient has opted out.
    treatment_group : int | None
        Optional numeric code for the patient's assigned treatment group.
    """

    __tablename__ = "apipatient"
    __table_args__ = {"schema": "noshow"}

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        index=True,
    )
    call_number: Mapped[int] = mapped_column(Integer, init=False, nullable=True)
    opt_out: Mapped[int] = mapped_column(Integer, init=False, nullable=True)
    treatment_group: Mapped[int] = mapped_column(Integer, init=False, nullable=True)


class ApiPrediction(Base):
    """ORM model for API predictions stored in noshow.apiprediction.

    Attributes
    ----------
    id : int
        Primary key for the prediction record.
    appointment_id : str
        External appointment identifier.
    prediction : float | None
        Predicted no-show probability for the appointment.
    start_time : datetime
        Scheduled start time of the appointment.
    clinic_name : str
        Name of the clinic.
    clinic_reception : str
        Clinic reception identifier or name.
    clinic_phone_number : str
        Clinic phone number.
    clinic_teleq_unit : str | None
        Optional teleq unit identifier.
    request_id : int
        Foreign key referencing the ApiRequest that produced this prediction.
    patient_id : str
        Foreign key referencing the ApiPatient this prediction is for.
    active : bool
        Whether the prediction is currently active.
    """

    __tablename__ = "apiprediction"
    __table_args__ = {"schema": "noshow"}

    id: Mapped[int] = mapped_column(
        primary_key=True, index=True, init=False, unique=True
    )
    appointment_id: Mapped[str] = mapped_column(String(50), index=True)
    prediction: Mapped[float] = mapped_column(Float, nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    clinic_name: Mapped[str]
    clinic_reception: Mapped[str]
    clinic_phone_number: Mapped[str]
    clinic_teleq_unit: Mapped[str] = mapped_column(String, nullable=True)
    clinic_actual_name: Mapped[str] = mapped_column(String(64), nullable=True)
    request_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(ApiRequest.id), init=False
    )
    patient_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey(ApiPatient.id),
        index=True,
    )
    active: Mapped[bool]

    request_relation: Mapped["ApiRequest"] = relationship()
    callresponse_relation: Mapped["ApiCallResponse"] = relationship(init=False)
    patient_relation: Mapped["ApiPatient"] = relationship()


class ApiSensitiveInfo(Base):
    """ORM model for sensitive patient information stored in noshow.apisensitiveinfo.

    Attributes
    ----------
    patient_id : str
        Primary key patient identifier (up to 64 characters).
    hix_number : str | None
        Health insurance number or identifier, optional.
    full_name : str
        Full name of the patient.
    first_name : str | None
        Patient's first name, optional.
    birth_date : date | None
        Patient's date of birth, optional.
    mobile_phone : str | None
        Patient's mobile phone number, optional.
    home_phone : str | None
        Patient's home phone number, optional.
    other_phone : str | None
        Any other contact phone number, optional.
    """

    __tablename__ = "apisensitiveinfo"
    __table_args__ = {"schema": "noshow"}

    patient_id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    hix_number: Mapped[str] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str]
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    birth_date: Mapped[date] = mapped_column(Date, nullable=True)
    mobile_phone: Mapped[str] = mapped_column(String, nullable=True)
    home_phone: Mapped[str] = mapped_column(String, nullable=True)
    other_phone: Mapped[str] = mapped_column(String, nullable=True)


class ApiCallResponse(Base):
    """ORM model for API call responses stored in noshow.apicallresponse.

    Attributes
    ----------
    id : int
        Primary key for the call response record.
    timestamp : datetime | None
        Time the call response was recorded.
    user : str | None
        Optional user identifier who handled the call.
    call_status : str
        Status of the call (e.g., reached, no_answer).
    call_outcome : str
        Outcome of the call (e.g., confirmed, cancelled).
    remarks : str
        Free-text remarks or notes about the call.
    prediction_id : int
        Foreign key referencing the ApiPrediction this response pertains to.
    """

    __tablename__ = "apicallresponse"
    __table_args__ = {"schema": "noshow"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, init=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=True, init=False)
    user: Mapped[str] = mapped_column(String(100), nullable=True, init=False)
    call_status: Mapped[str]
    call_outcome: Mapped[str]
    remarks: Mapped[str]
    prediction_id: Mapped[int] = mapped_column(ForeignKey(ApiPrediction.id))
