from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta

from sqlalchemy import JSON, Column, DateTime, String, create_engine, select
from sqlalchemy.orm import Session, declarative_base

from app.models import AuditRequest, AuditResponse

Base = declarative_base()


class AuditCache(Base):
    __tablename__ = "audit_cache"

    cache_key = Column(String, primary_key=True)
    payload = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class CacheStore:
    def __init__(self, database_url: str = "sqlite:///./rxtrust.db", ttl_hours: int = 24) -> None:
        self.engine = create_engine(database_url, future=True)
        Base.metadata.create_all(self.engine)
        self.ttl = timedelta(hours=ttl_hours)

    @staticmethod
    def key_from_request(request: AuditRequest) -> str:
        payload = f"{request.product_name}|{request.batch_number}|{request.manufacturer}".lower()
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def get(self, request: AuditRequest) -> AuditResponse | None:
        key = self.key_from_request(request)
        now = datetime.utcnow()
        with Session(self.engine) as session:
            cached = session.scalar(select(AuditCache).where(AuditCache.cache_key == key))
            if not cached:
                return None
            if now - cached.updated_at > self.ttl:
                return None
            data = json.loads(json.dumps(cached.payload))
            data["cached"] = True
            return AuditResponse.model_validate(data)

    def set(self, request: AuditRequest, response: AuditResponse) -> None:
        key = self.key_from_request(request)
        with Session(self.engine) as session:
            cached = session.scalar(select(AuditCache).where(AuditCache.cache_key == key))
            payload = response.model_dump(mode="json")
            if cached:
                cached.payload = payload
                cached.updated_at = datetime.utcnow()
            else:
                session.add(
                    AuditCache(cache_key=key, payload=payload, updated_at=datetime.utcnow())
                )
            session.commit()
