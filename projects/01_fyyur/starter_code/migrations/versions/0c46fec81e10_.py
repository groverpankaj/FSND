"""empty message

Revision ID: 0c46fec81e10
Revises: 5849ba5eddaa
Create Date: 2019-10-31 10:11:50.014798

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c46fec81e10'
down_revision = '5849ba5eddaa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('artist_time_begin', sa.Time(), nullable=True))
    op.add_column('Artist', sa.Column('artist_time_end', sa.Time(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'artist_time_end')
    op.drop_column('Artist', 'artist_time_begin')
    # ### end Alembic commands ###
