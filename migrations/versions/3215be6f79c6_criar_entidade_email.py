"""criar_entidade_email

Revision ID: 3215be6f79c6
Revises: 5bae7dace858
Create Date: 2025-11-11 22:06:09.898826

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3215be6f79c6'
down_revision: Union[str, None] = '5bae7dace858'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'Email',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('email', sa.String(), nullable=False, unique=True),
    )


def downgrade() -> None:
    op.drop_table("Email")
