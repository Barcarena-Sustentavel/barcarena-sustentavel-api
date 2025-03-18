"""Titulo grafico adicionado

Revision ID: 171ac2610709
Revises: 007009e24d03
Create Date: 2025-03-15 14:09:30.160550

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '171ac2610709'
down_revision: Union[str, None] = '007009e24d03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('Anexo', 
        sa.Column('tituloGrafico', sa.String(), nullable=True),
        schema='barcarena_sustentavel'
    )

def downgrade() -> None:
    op.drop_column('Anexo', 'tituloGrafico', schema='barcarena_sustentavel')
    
