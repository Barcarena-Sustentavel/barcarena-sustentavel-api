"""create_model_estudoComplementar

Revision ID: b180697184de
Revises: bb1f56f43b6d
Create Date: 2025-10-01 10:12:00.463008

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b180697184de'
down_revision: Union[str, None] = 'bb1f56f43b6d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'EstudoComplementar',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.Column('fkDimensao_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['fkDimensao_id'], ['barcarena_sustentavel.Dimensao.id']),
    )
    op.add_column('Anexo',
        sa.Column('fkEstudoComplementar_id', sa.Integer(), nullable=True),
        schema='barcarena_sustentavel'
    )


def downgrade() -> None:
    op.drop_table("EstudoComplementar", schema="barcarena_sustentavel")
