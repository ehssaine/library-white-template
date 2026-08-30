"""Transition-matrix data model — SQLAlchemy 2.0 / PostgreSQL.

The Excel workbook holds 4 matrices identified by (ECHELLE, MODEL). Each
Excel line is one matrix row (Plot = from-rating) and the numbered columns
1..9 are the to-rating probabilities:

    ttc_matrix ──< ttc_matrix_row ──< ttc_matrix_cell
    (echelle, model)  (plot, effectifs,   (col, proba)
                       dernier_eff_pit, std)

Variable dimensions (8x9 / 7x8) fall out naturally: a matrix simply has
as many rows / cells as were loaded.
"""

import enum

from sqlalchemy import (
    CheckConstraint,
    Double,
    Enum,
    ForeignKey,
    Identity,
    Integer,
    SmallInteger,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Echelle(str, enum.Enum):
    PC = "PC"
    PR = "PR"
    PP = "PP"
    PI = "PI"


class ShiftModel(str, enum.Enum):
    # member names == values so the DB stores exactly what the file contains
    shift_LCorp = "shift_LCorp"
    shift_IFA = "shift_IFA"


class TtcMatrix(Base):
    """One matrix of the workbook = one (echelle, model) pair."""

    __tablename__ = "ttc_matrix"
    __table_args__ = (
        UniqueConstraint("echelle", "model", name="uq_ttc_matrix_echelle_model"),
    )

    id_mx: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    echelle: Mapped[Echelle] = mapped_column(Enum(Echelle, name="echelle"), nullable=False)
    model: Mapped[ShiftModel] = mapped_column(Enum(ShiftModel, name="shift_model"), nullable=False)

    rows: Mapped[list["TtcMatrixRow"]] = relationship(
        back_populates="matrix",
        order_by="TtcMatrixRow.plot",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Links from the first sketch (1 TTC -> * children)
    static_matrices: Mapped[list["StaticMatrix"]] = relationship(
        back_populates="ttc_matrix", passive_deletes=True
    )
    pd_irba_rows: Mapped[list["PdIrba"]] = relationship(
        back_populates="ttc_matrix", passive_deletes=True
    )
    adjusted_matrices: Mapped[list["AdjustedMatrix"]] = relationship(
        back_populates="ttc_matrix", passive_deletes=True
    )


class TtcMatrixRow(Base):
    """One Excel line: the from-rating (Plot) with its headcounts."""

    __tablename__ = "ttc_matrix_row"
    __table_args__ = (
        UniqueConstraint("id_mx", "plot", name="uq_ttc_matrix_row_plot"),
    )

    id_row: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    id_mx: Mapped[int] = mapped_column(
        ForeignKey("ttc_matrix.id_mx", ondelete="CASCADE"), nullable=False
    )
    plot: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # Excel "Plot" (1..8)
    effectifs: Mapped[int] = mapped_column(Integer, nullable=False)  # EFFECTIFS
    dernier_eff_pit: Mapped[int] = mapped_column(Integer, nullable=False)  # DERNIER_EFF_PIT
    # STD is 4 on every line of the file — move it to TtcMatrix if it is matrix-level
    std: Mapped[float] = mapped_column(Double, nullable=False)

    matrix: Mapped["TtcMatrix"] = relationship(back_populates="rows")
    cells: Mapped[list["TtcMatrixCell"]] = relationship(
        back_populates="row",
        order_by="TtcMatrixCell.col",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class TtcMatrixCell(Base):
    """One probability: from-rating (row) x to-rating (numbered column)."""

    __tablename__ = "ttc_matrix_cell"
    __table_args__ = (
        CheckConstraint("proba >= 0 AND proba <= 1", name="ck_ttc_matrix_cell_proba"),
    )

    id_row: Mapped[int] = mapped_column(
        ForeignKey("ttc_matrix_row.id_row", ondelete="CASCADE"), primary_key=True
    )
    col: Mapped[int] = mapped_column(SmallInteger, primary_key=True)  # Excel header 1..9
    proba: Mapped[float] = mapped_column(Double, nullable=False)

    row: Mapped["TtcMatrixRow"] = relationship(back_populates="cells")


# --- Unchanged from the first sketch ---------------------------------------


class StaticMatrix(Base):
    __tablename__ = "static_matrix"

    id_sp: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    id_mx: Mapped[int] = mapped_column(
        ForeignKey("ttc_matrix.id_mx", ondelete="CASCADE"), nullable=False, index=True
    )
    # ... other STATIC_MATRIX columns

    ttc_matrix: Mapped["TtcMatrix"] = relationship(back_populates="static_matrices")


class PdIrba(Base):
    __tablename__ = "pd_irba"

    id_irba: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    id_mx: Mapped[int] = mapped_column(
        ForeignKey("ttc_matrix.id_mx", ondelete="CASCADE"), nullable=False, index=True
    )
    # ... other PD_IRBA columns

    ttc_matrix: Mapped["TtcMatrix"] = relationship(back_populates="pd_irba_rows")


class AdjustedMatrix(Base):
    __tablename__ = "adjusted_matrix"

    id_adjusted: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    id_mx: Mapped[int] = mapped_column(
        ForeignKey("ttc_matrix.id_mx", ondelete="CASCADE"), nullable=False, index=True
    )
    # ... other ADJUSTED_MATRIX columns

    ttc_matrix: Mapped["TtcMatrix"] = relationship(back_populates="adjusted_matrices")
