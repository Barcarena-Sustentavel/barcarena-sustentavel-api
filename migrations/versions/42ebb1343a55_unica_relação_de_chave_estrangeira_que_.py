"""unica relação de chave estrangeira que não permite nulo em anexo é a com a dimensão

Revision ID: 42ebb1343a55
Revises: 92f34c7eb2de
Create Date: 2025-02-17 11:42:25.524857

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '42ebb1343a55'
down_revision: Union[str, None] = '92f34c7eb2de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.alter_column('Anexo', 'fkDimensao_id',
                    nullable=False,
                    existing_type=sa.ForeignKey('barcarena_sustentavel.Dimensao.id'))
    op.alter_column('Anexo', 'fkKML_id',
                    nullable=True,
                    existing_type=sa.ForeignKey('barcarena_sustentavel.KML.id'))
    op.alter_column('Anexo', 'fkIndicador_id',
                    nullable=True,
                    existing_type=sa.ForeignKey('barcarena_sustentavel.Indicador.id'))
    op.alter_column('Anexo', 'fkContribuicao_id',
                    nullable=True,
                    existing_type=sa.ForeignKey('barcarena_sustentavel.Contribuicao.id'))


def downgrade() -> None:
    op.alter_column('Anexo', 'fkDimensao_id',
                    nullable=True,
                    existing_type=sa.ForeignKey('barcarena_sustentavel.Dimensao.id'))
    op.alter_column('Anexo', 'fkIndicador_id',
                    nullable=True,
                    existing_type=sa.ForeignKey('barcarena_sustentavel.Indicador.id'))
    op.alter_column('Anexo', 'fkContribuicao_id',
                    nullable=True,
                    existing_type=sa.ForeignKey('barcarena_sustentavel.Contribuicao.id'))

