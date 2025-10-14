"""renomear_name_nome_estudoComplementar

Revision ID: 5bae7dace858
Revises: 9f75a98a50f0
Create Date: 2025-10-14 10:57:51.085732

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5bae7dace858'
down_revision: Union[str, None] = '9f75a98a50f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column(
        "EstudoComplementar",
        "name",
        new_column_name="nome",
        schema="barcarena_sustentavel"
    )


def downgrade():
    op.alter_column(
        "EstudoComplementar",
        "nome",
        new_column_name="name",
        schema="barcarena_sustentavel"
    )
