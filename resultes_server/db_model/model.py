from pathlib import Path
from typing import List
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import URL
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    type_annotation_map = {Path: String(), URL: String()}


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]
    simulations: Mapped[List["Simulation"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"


class Simulation(Base):
    __tablename__ = "simulation"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="simulations")

    variations: Mapped[List["Variation"]] = relationship(
        back_populates="simulation", cascade="all, delete-orphan"
    )


class Variation(Base):
    __tablename__ = "variation"
    id: Mapped[int] = mapped_column(primary_key=True)
    simulation_id: Mapped[int] = mapped_column(ForeignKey("simulation.id"))
    simulation: Mapped["User"] = relationship(back_populates="variations")

    dir_path: Mapped[Path]
    url: Mapped[URL]

    def __repr__(self) -> str:
        return f"Variation(id={self.id!r}, dir_path={self.dir_path!r}, url={self.url!r})"
