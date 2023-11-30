"""empty message

Revision ID: 01db48c9b2c9
Revises: 
Create Date: 2023-10-12 20:13:36.181361

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '01db48c9b2c9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('last_seen', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('last_seen')

    # ### end Alembic commands ###
