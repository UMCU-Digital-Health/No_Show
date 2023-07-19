from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
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
    __table_args__ = {"schema": "no_show"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, init=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime)
    response_code: Mapped[int] = mapped_column(Integer, index=True)
    response_message: Mapped[str]
    endpoint: Mapped[str]
    runtime: Mapped[float]
    api_version: Mapped[str]


class ApiPrediction(Base):
    __tablename__ = "apiprediction"
    __table_args__ = {"schema": "no_show"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, init=False)
    patient_id: Mapped[str] = mapped_column(String, index=True)
    prediction: Mapped[float]
    call_order: Mapped[int]
    start_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    request_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(ApiRequest.id), init=False
    )
    request_relation: Mapped["ApiRequest"] = relationship()
    sensitiveinfo_relation: Mapped["ApiSensitiveInfo"] = relationship()
    callresponse_relation: Mapped["ApiCallResponse"] = relationship(init=False)


class ApiSensitiveInfo(Base):
    __tablename__ = "apisensitiveinfo"
    __table_args__ = {"schema": "no_show"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, init=False)
    full_name: Mapped[str]
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    mobile_phone: Mapped[str] = mapped_column(String, nullable=True)
    home_phone: Mapped[str] = mapped_column(String, nullable=True)
    other_phone: Mapped[str] = mapped_column(String, nullable=True)
    clinic_reception: Mapped[str]
    clinic_phone_number: Mapped[str]
    prediction_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(ApiPrediction.id), init=False
    )


class ApiCallResponse(Base):
    __tablename__ = "apicallresponse"
    __table_args__ = {"schema": "no_show"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, init=False)
    call_status: Mapped[str]
    call_outcome: Mapped[str]
    remarks: Mapped[str]
    prediction_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(ApiPrediction.id), init=False
    )
