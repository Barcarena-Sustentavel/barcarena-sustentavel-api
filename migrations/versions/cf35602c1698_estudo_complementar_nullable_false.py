"""estudo_complementar_nullable_false

Revision ID: cf35602c1698
Revises: 5bae7dace858
Create Date: 2025-10-29 10:20:44.908360

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf35602c1698'
down_revision: Union[str, None] = '5bae7dace858'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("EstudoComplementar", "fkDimensao_id",nullable=True, schema="barcarena_sustentavel")
    op.alter_column("Anexo", "fkDimensao_id",nullable=True, schema="barcarena_sustentavel")

def downgrade() -> None:
    op.alter_column("EstudoComplementar", "fkDimensao_id",nullable=False, schema="barcarena_sustentavel")
    op.alter_column("Anexo", "fkDimensao_id",nullable=False, schema="barcarena_sustentavel")
