"""empty message

Revision ID: 19d1c51c479d
Revises: b42baf10d9bf
Create Date: 2023-10-19 22:47:20.252629

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '19d1c51c479d'
down_revision = 'b42baf10d9bf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transit', schema=None) as batch_op:
        batch_op.add_column(sa.Column('s_p', sa.String(length=5), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transit', schema=None) as batch_op:
        batch_op.drop_column('s_p')

    # ### end Alembic commands ###
