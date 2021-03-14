"""dogs table

Revision ID: a00078b6f146
Revises: 935ee3787f33
Create Date: 2021-03-14 09:55:00.475610

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a00078b6f146'
down_revision = '935ee3787f33'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dog',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dog_name', sa.String(length=140), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dog_timestamp'), 'dog', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_dog_timestamp'), table_name='dog')
    op.drop_table('dog')
    # ### end Alembic commands ###
