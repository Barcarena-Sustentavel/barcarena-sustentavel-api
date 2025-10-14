"""criar_posicao

Revision ID: 9f75a98a50f0
Revises: b180697184de
Create Date: 2025-10-13 19:19:24.810901

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f75a98a50f0'
down_revision: Union[str, None] = 'b180697184de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.create_table(
        'Posicao',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('posicao', sa.Integer, nullable=False),
        sa.Column('fkIndicador_id', sa.Integer, sa.ForeignKey('barcarena_sustentavel.Indicador.id'), nullable=True),
        sa.Column('fkAnexo_id', sa.Integer, sa.ForeignKey('barcarena_sustentavel.Anexo.id'), nullable=True),
        sa.ForeignKeyConstraint(['fkIndicador_id'], ['barcarena_sustentavel.Indicador.id']),
        sa.ForeignKeyConstraint(['fkAnexo_id'], ['barcarena_sustentavel.Anexo.id']),
        schema='barcarena_sustentavel'
    )


def downgrade():
    op.drop_table('Posicao', schema='barcarena_sustentavel')
