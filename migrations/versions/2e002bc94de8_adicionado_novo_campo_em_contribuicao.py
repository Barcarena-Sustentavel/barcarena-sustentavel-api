"""adicionado novo campo em Contribuicao

Revision ID: 2e002bc94de8
Revises: 42ebb1343a55
Create Date: 2025-02-25 13:17:45.781185

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e002bc94de8'
down_revision: Union[str, None] = '42ebb1343a55'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('Contribuicao', 
        sa.Column('path', sa.String(), nullable=True),
        schema='barcarena_sustentavel'
    )

def downgrade() -> None:
    op.drop_column('Contribuicao', 'path', schema='barcarena_sustentavel'
    )
    #pass
