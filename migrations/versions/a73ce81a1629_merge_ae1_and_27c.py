"""merge ae1 and 27c

Revision ID: a73ce81a1629
Revises: 3215be6f79c6, cf35602c1698
Create Date: 2025-12-02 15:40:01.433545

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a73ce81a1629'
down_revision: Union[str, None] = ('3215be6f79c6', 'cf35602c1698')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
