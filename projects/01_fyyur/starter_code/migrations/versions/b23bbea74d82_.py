"""empty message

Revision ID: b23bbea74d82
Revises: 25801a711793
Create Date: 2019-10-31 10:36:36.120994

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b23bbea74d82'
down_revision = '25801a711793'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('artist_date_begin', sa.Date(), nullable=True))
    op.add_column('Artist', sa.Column('artist_date_end', sa.Date(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'artist_date_end')
    op.drop_column('Artist', 'artist_date_begin')
    # ### end Alembic commands ###
