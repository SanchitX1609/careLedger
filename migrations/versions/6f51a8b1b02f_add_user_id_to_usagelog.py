"""Add user_id to UsageLog

Revision ID: 6f51a8b1b02f
Revises: 
Create Date: 2025-06-07 05:44:29.740745

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f51a8b1b02f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('usage_logs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_usage_logs_user_id_users', 'users', ['user_id'], ['id']) # Added constraint name

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('usage_logs', schema=None) as batch_op:
        batch_op.drop_constraint('fk_usage_logs_user_id_users', type_='foreignkey') # Added constraint name
        batch_op.drop_column('user_id')

    # ### end Alembic commands ###
