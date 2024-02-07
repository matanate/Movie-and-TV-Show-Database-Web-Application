"""add img_url to movies anf tvshows

Revision ID: 720f9bfc934d
Revises: bd6e78e04ed3
Create Date: 2024-01-31 15:53:32.964878

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '720f9bfc934d'
down_revision = 'bd6e78e04ed3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('movies', schema=None) as batch_op:
        batch_op.add_column(sa.Column('img_url', sa.String(length=200), nullable=False))

    with op.batch_alter_table('tv_shows', schema=None) as batch_op:
        batch_op.add_column(sa.Column('img_url', sa.String(length=200), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tv_shows', schema=None) as batch_op:
        batch_op.drop_column('img_url')

    with op.batch_alter_table('movies', schema=None) as batch_op:
        batch_op.drop_column('img_url')

    # ### end Alembic commands ###