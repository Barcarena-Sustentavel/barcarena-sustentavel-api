"""dimensao_posicao

Revision ID: c3c57b317d4f
Revises: 0a1ae7c1337b
Create Date: 2026-03-22 11:34:33.489319

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3c57b317d4f'
down_revision: Union[str, None] = '0a1ae7c1337b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
    "Posicao",
    sa.Column("fkDimensao_id", sa.Integer(), sa.ForeignKey("Dimensao.id"), nullable=True))


def downgrade() -> None:
    op.drop_column("Posicao","fkDimensao_id")
