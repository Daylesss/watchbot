"""empty message

Revision ID: 7853085156f7
Revises: bb9a59358bb6
Create Date: 2024-01-16 14:28:13.645582

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7853085156f7'
down_revision = 'bb9a59358bb6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('transaction', sa.Column('tg_id', sa.Integer(), nullable=False))
    op.add_column('transaction', sa.Column('transaction_time', sa.TIMESTAMP(), nullable=True))
    op.drop_constraint('watch_file_unique_file_id_fkey', 'watch_file', type_='foreignkey')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key('watch_file_unique_file_id_fkey', 'watch_file', 'watch', ['unique_file_id'], ['unique_file_id'])
    op.drop_column('transaction', 'transaction_time')
    op.drop_column('transaction', 'tg_id')
    # ### end Alembic commands ###
