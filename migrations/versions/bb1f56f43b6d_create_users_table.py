import sqlalchemy as sa
from alembic import op
import bcrypt

# revision identifiers, used by Alembic.
revision: str = 'bb1f56f43b6d'
down_revision: str | None = '171ac2610709'
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        'User',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('username', sa.String(), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
    )

    # Gera hash para a senha padrão
    password = "barcarena_sustentavel".encode("utf-8")
    hashed = bcrypt.hashpw(password, bcrypt.gensalt()).decode("utf-8")

    # Insere usuário inicial com e-mail e senha hash
    op.execute(
        sa.text(
            "INSERT INTO \"User\" (username, hashed_password) VALUES (:username, :hashed_password)"
        ).params(username="barcarena_sustentavel", hashed_password=hashed)
    )

def downgrade() -> None:
    op.drop_table('User')
