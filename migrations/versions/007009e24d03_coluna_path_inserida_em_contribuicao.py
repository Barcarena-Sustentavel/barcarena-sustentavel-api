"""coluna path inserida em contribuicao

Revision ID: 007009e24d03
Revises: 2e002bc94de8
Create Date: 2025-02-27 13:32:21.910071

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '007009e24d03'
down_revision: Union[str, None] = '2e002bc94de8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
