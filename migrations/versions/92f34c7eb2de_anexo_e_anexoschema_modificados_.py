"""Anexo e AnexoSchema modificados, atributos de descrição e tipo de gráficos adicionados

Revision ID: 92f34c7eb2de
Revises: 0409d05e077a
Create Date: 2025-02-17 11:37:06.282101

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '92f34c7eb2de'
down_revision: Union[str, None] = '0409d05e077a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('Anexo', 
        sa.Column('tipoGrafico', sa.String(), nullable=True),
        schema='barcarena_sustentavel'
    )
    op.add_column('Anexo',
        sa.Column('descricaoGrafico', sa.String(), nullable=True),
        schema='barcarena_sustentavel'
    )


def downgrade() -> None:
    op.drop_column('Anexo', 'tipoGrafico', schema='barcarena_sustentavel')
    op.drop_column('Anexo', 'descricaoGrafico', schema='barcarena_sustentavel')

