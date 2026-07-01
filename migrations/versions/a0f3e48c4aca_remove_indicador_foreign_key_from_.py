"""remove_indicador_foreign_key_from_referencias

Revision ID: a0f3e48c4aca
Revises: 5bc263c39d32
Create Date: 2026-06-30 21:35:05.925517

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a0f3e48c4aca'
down_revision: Union[str, None] = '5bc263c39d32'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Remove a restrição de Chave Estrangeira (Foreign Key) primeiro
    # Nota: O nome padrão da constraint costuma ser 'fk_Referencias_fkIndicador_id_Indicador' 
    # ou semelhante. Se o seu banco der erro de "constraint not found", verifique o nome exato dela no seu DB.
    op.drop_constraint(
        'Referencias_fkIndicador_id_fkey', 
        'Referencias', 
        schema="barcarena_sustentavel", 
        type_='foreignkey'
    )
    
    # 2. Agora remove a coluna física do banco de dados


def downgrade() -> None:
    # Caso precise reverter, adiciona a coluna de volta
    op.add_column(
        'Referencias', 
        sa.Column('fkIndicador_id', sa.Integer(), nullable=True), 
        schema="barcarena_sustentavel"
    )
    
    # Cria a restrição de chave estrangeira novamente
    op.create_foreign_key(
        'fk_Referencias_fkIndicador_id_Indicador',
        source_table='Referencias',
        referent_table='Indicador',
        local_cols=['fkIndicador_id'],
        remote_cols=['id'],
        source_schema="barcarena_sustentavel",
        referent_schema="barcarena_sustentavel"
    )