"""indicador_fonte_metodologia

Revision ID: 0a1ae7c1337b
Revises: 62ec90ecd484
Create Date: 2026-03-20 15:23:51.768457

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0a1ae7c1337b'
down_revision: Union[str, None] = '62ec90ecd484'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("Indicador", sa.Column("periodicidade", sa.String(), nullable=False, server_default=""))
    op.add_column("Indicador", sa.Column("ultimaAtualizacao", sa.String(), nullable=False, server_default=""))
    op.add_column("Indicador", sa.Column("unidadeMedida", sa.String(), nullable=False, server_default=""))
    op.add_column("Indicador", sa.Column("metodologia", sa.String(), nullable=False, server_default=""))
    op.add_column("Referencias", sa.Column("fkIndicador_id", sa.Integer(),sa.ForeignKey("Indicador.id") ,nullable=True, server_default=None))
    pass    


def downgrade() -> None:
    op.drop_column("sua_tabela", "periodicidade")
    op.drop_column("sua_tabela", "ultimaAtualizacao")
    op.drop_column("sua_tabela", "unidadeMedida")
    op.drop_column("sua_tabela", "metodologia")
    op.drop_constraint("fk_referencias_fkIndicador_id", "Referencias", type_="foreignkey")
    op.drop_column("Referencias", "fkIndicador_id")
    pass
