"""create dimensao and related tables

Revision ID: 0409d05e077a
Revises: 
Create Date: 2025-01-22 12:47:59.952253

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0409d05e077a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Criando o schema barcarena_sustentavel se não existir
    op.execute('CREATE SCHEMA IF NOT EXISTS barcarena_sustentavel')

    # Criação das tabelas no schema barcarena_sustentavel
    op.create_table(
        'Dimensao',
        sa.Column('nome', sa.Text, nullable=False),
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('descricao', sa.Text),
        schema='barcarena_sustentavel'
    )

    op.create_index(
        'pk_dimensoes_dimensaomodel',
        'Dimensao',
        ['id', 'nome'],
        unique=True,
        schema='barcarena_sustentavel'
    )

    op.create_table(
        'Indicador',
        sa.Column('fkDimensao_id', sa.Integer, nullable=False),
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('nome', sa.Text, nullable=False),
        sa.ForeignKeyConstraint(['fkDimensao_id'], ['barcarena_sustentavel.Dimensao.id']),
        schema='barcarena_sustentavel'
    )

    op.create_table(
        'KML',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.Text, nullable=False),
        sa.Column('fkDimensao_id', sa.Integer, nullable=False),
        sa.ForeignKeyConstraint(['fkDimensao_id'], ['barcarena_sustentavel.Dimensao.id']),
        schema='barcarena_sustentavel'
    )

    op.create_table(
        'Referencias',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('nome', sa.Text, nullable=False),
        sa.Column('link', sa.Text),
        sa.Column('fkDimensao_id', sa.Integer, nullable=False),
        sa.ForeignKeyConstraint(['fkDimensao_id'], ['barcarena_sustentavel.Dimensao.id']),
        schema='barcarena_sustentavel'
    )

    op.create_table(
        'Contribuicao',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('nome', sa.Text),
        sa.Column('email', sa.Text),
        sa.Column('telefone', sa.Text),
        sa.Column('comentario', sa.Text, nullable=False),
        sa.Column('fkDimensao_id', sa.Integer, nullable=False),
        sa.ForeignKeyConstraint(['fkDimensao_id'], ['barcarena_sustentavel.Dimensao.id']),
        schema='barcarena_sustentavel'
    )

    op.create_table(
        'Anexo',
        sa.Column('path', sa.Text, nullable=False),
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('fkDimensao_id', sa.Integer),
        sa.Column('fkKml_id', sa.Integer, nullable=False),
        sa.Column('fkIndicador_id', sa.Integer),
        sa.Column('fkContribuicao_id', sa.Integer),
        sa.ForeignKeyConstraint(['fkDimensao_id'], ['barcarena_sustentavel.Dimensao.id']),
        sa.ForeignKeyConstraint(['fkContribuicao_id'], ['barcarena_sustentavel.Contribuicao.id']),
        sa.ForeignKeyConstraint(['fkKml_id'], ['barcarena_sustentavel.KML.id']),
        schema='barcarena_sustentavel'
    )

    op.create_index(
        'unq_Anexo_fkKml_id',
        'Anexo',
        ['fkKml_id'],
        unique=True,
        schema='barcarena_sustentavel'
    )


def downgrade() -> None:
    # Removendo as tabelas e schema
    op.drop_table('Anexo', schema='barcarena_sustentavel')
    op.drop_table('Contribuicao', schema='barcarena_sustentavel')
    op.drop_table('Referencias', schema='barcarena_sustentavel')
    op.drop_table('KML', schema='barcarena_sustentavel')
    op.drop_table('Indicador', schema='barcarena_sustentavel')
    op.drop_table('Dimensao', schema='barcarena_sustentavel')
    op.execute('DROP SCHEMA IF EXISTS barcarena_sustentavel CASCADE')
