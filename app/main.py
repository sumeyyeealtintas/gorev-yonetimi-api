"""Görev Yönetimi API'si - FastAPI + SQLAlchemy + SQLite."""
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import DateTime, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool

import os

VERITABANI_URL = os.getenv("DATABASE_URL", "sqlite:///./gorevler.db")


def _motor_olustur(url: str):
    if url.startswith("sqlite"):
        kwargs = {"connect_args": {"check_same_thread": False}}
        if ":memory:" in url:
            kwargs["poolclass"] = StaticPool
        return create_engine(url, **kwargs)
    return create_engine(url)


motor = _motor_olustur(VERITABANI_URL)
OturumFabrikasi = sessionmaker(bind=motor, autoflush=False)


class Taban(DeclarativeBase):
    pass


class Durum(str, Enum):
    yapilacak = "yapilacak"
    devam_ediyor = "devam_ediyor"
    tamamlandi = "tamamlandi"


class Gorev(Taban):
    __tablename__ = "gorevler"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    baslik: Mapped[str] = mapped_column(String(120))
    aciklama: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    durum: Mapped[str] = mapped_column(String(20), default=Durum.yapilacak.value)
    oncelik: Mapped[int] = mapped_column(Integer, default=3)
    olusturulma: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


class GorevOlustur(BaseModel):
    baslik: str = Field(min_length=1, max_length=120, examples=["Rapor yaz"])
    aciklama: Optional[str] = Field(default=None, max_length=500)
    oncelik: int = Field(default=3, ge=1, le=5, description="1 = en yüksek, 5 = en düşük")


class GorevGuncelle(BaseModel):
    baslik: Optional[str] = Field(default=None, min_length=1, max_length=120)
    aciklama: Optional[str] = Field(default=None, max_length=500)
    durum: Optional[Durum] = None
    oncelik: Optional[int] = Field(default=None, ge=1, le=5)


class GorevCikti(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    baslik: str
    aciklama: Optional[str]
    durum: Durum
    oncelik: int
    olusturulma: datetime


app = FastAPI(
    title="Görev Yönetimi API",
    description="Görevleri oluşturma, listeleme, güncelleme ve silme işlemleri.",
    version="1.0.0",
)
Taban.metadata.create_all(motor)


def oturum_al():
    oturum = OturumFabrikasi()
    try:
        yield oturum
    finally:
        oturum.close()


def _bul_veya_404(oturum: Session, gorev_id: int) -> Gorev:
    gorev = oturum.get(Gorev, gorev_id)
    if gorev is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Görev bulunamadı")
    return gorev


@app.get("/saglik", tags=["Sistem"])
def saglik():
    return {"durum": "ok"}


@app.post("/gorevler", response_model=GorevCikti, status_code=201, tags=["Görevler"])
def gorev_olustur(veri: GorevOlustur, oturum: Session = Depends(oturum_al)):
    gorev = Gorev(**veri.model_dump())
    oturum.add(gorev)
    oturum.commit()
    oturum.refresh(gorev)
    return gorev


@app.get("/gorevler", response_model=list[GorevCikti], tags=["Görevler"])
def gorevleri_listele(
    durum: Optional[Durum] = None,
    arama: Optional[str] = Query(default=None, description="Başlıkta arar"),
    sayfa: int = Query(default=1, ge=1),
    boyut: int = Query(default=10, ge=1, le=100),
    oturum: Session = Depends(oturum_al),
):
    sorgu = select(Gorev).order_by(Gorev.oncelik, Gorev.id)
    if durum:
        sorgu = sorgu.where(Gorev.durum == durum.value)
    if arama:
        sorgu = sorgu.where(Gorev.baslik.ilike(f"%{arama}%"))
    sorgu = sorgu.offset((sayfa - 1) * boyut).limit(boyut)
    return oturum.scalars(sorgu).all()


@app.get("/gorevler/{gorev_id}", response_model=GorevCikti, tags=["Görevler"])
def gorev_getir(gorev_id: int, oturum: Session = Depends(oturum_al)):
    return _bul_veya_404(oturum, gorev_id)


@app.patch("/gorevler/{gorev_id}", response_model=GorevCikti, tags=["Görevler"])
def gorev_guncelle(gorev_id: int, veri: GorevGuncelle, oturum: Session = Depends(oturum_al)):
    gorev = _bul_veya_404(oturum, gorev_id)
    for alan, deger in veri.model_dump(exclude_unset=True).items():
        setattr(gorev, alan, deger.value if isinstance(deger, Durum) else deger)
    oturum.commit()
    oturum.refresh(gorev)
    return gorev


@app.delete("/gorevler/{gorev_id}", status_code=204, tags=["Görevler"])
def gorev_sil(gorev_id: int, oturum: Session = Depends(oturum_al)):
    oturum.delete(_bul_veya_404(oturum, gorev_id))
    oturum.commit()
