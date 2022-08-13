"""empty message

Revision ID: 277493f1afd3
Revises: 1dd178acb257
Create Date: 2022-08-13 15:38:50.674049

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '277493f1afd3'
down_revision = '1dd178acb257'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('show', sa.Column('venue_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'show', 'venue', ['venue_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'show', type_='foreignkey')
    op.drop_column('show', 'venue_id')
    # ### end Alembic commands ###
