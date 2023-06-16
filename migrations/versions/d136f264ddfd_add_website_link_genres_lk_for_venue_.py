"""add website_link/genres/lk_for_venue-artis for Venue and Artist models

Revision ID: d136f264ddfd
Revises: 06dc2fd8cf7a
Create Date: 2023-06-16 21:35:23.401397

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd136f264ddfd'
down_revision = '06dc2fd8cf7a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Artist', schema=None) as batch_op:
        batch_op.add_column(sa.Column('website_link', sa.String(length=250), nullable=True))
        batch_op.add_column(sa.Column('seeking_description', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('looking_for_venue', sa.Boolean(), nullable=True))

    with op.batch_alter_table('Venue', schema=None) as batch_op:
        batch_op.add_column(sa.Column('website_link', sa.String(length=250), nullable=True))
        batch_op.add_column(sa.Column('genres', sa.ARRAY(sa.String(length=120)), nullable=True))
        batch_op.add_column(sa.Column('seeking_description', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('looking_for_talent', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Venue', schema=None) as batch_op:
        batch_op.drop_column('looking_for_talent')
        batch_op.drop_column('seeking_description')
        batch_op.drop_column('genres')
        batch_op.drop_column('website_link')

    with op.batch_alter_table('Artist', schema=None) as batch_op:
        batch_op.drop_column('looking_for_venue')
        batch_op.drop_column('seeking_description')
        batch_op.drop_column('website_link')

    # ### end Alembic commands ###
