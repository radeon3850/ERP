"""empty message

Revision ID: a2cfaf823aa8
Revises: 01db48c9b2c9
Create Date: 2023-10-14 00:15:39.586406

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a2cfaf823aa8'
down_revision = '01db48c9b2c9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('statistics_user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('factor_price', sa.REAL(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('statistics_user', schema=None) as batch_op:
        batch_op.drop_column('factor_price')

    # ### end Alembic commands ###