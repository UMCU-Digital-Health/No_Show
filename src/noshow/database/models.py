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
    pass


class ApiRequest(Base):
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
    __tablename__ = "apipatient"
    __table_args__ = {"schema": "noshow"}

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        index=True,
    )
    call_number: Mapped[int] = mapped_column(Integer, init=False, nullable=True)


class ApiPrediction(Base):
    __tablename__ = "apiprediction"
    __table_args__ = {"schema": "noshow"}

    id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    prediction: Mapped[float] = mapped_column(Float, nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    clinic_name: Mapped[str]
    clinic_reception: Mapped[str]
    clinic_phone_number: Mapped[str]
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
    __tablename__ = "apisensitiveinfo"
    __table_args__ = {"schema": "noshow"}

    patient_id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    full_name: Mapped[str]
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    birth_date: Mapped[date] = mapped_column(Date, nullable=True)
    mobile_phone: Mapped[str] = mapped_column(String, nullable=True)
    home_phone: Mapped[str] = mapped_column(String, nullable=True)
    other_phone: Mapped[str] = mapped_column(String, nullable=True)


class ApiCallResponse(Base):
    __tablename__ = "apicallresponse"
    __table_args__ = {"schema": "noshow"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, init=False)
    call_status: Mapped[str]
    call_outcome: Mapped[str]
    remarks: Mapped[str]
    prediction_id: Mapped[str] = mapped_column(String(50), ForeignKey(ApiPrediction.id))
