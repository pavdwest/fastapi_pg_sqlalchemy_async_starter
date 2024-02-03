"""Create Review Model

Revision ID: 829f639ffb10
Revises: 6360d085c2af
Create Date: 2023-11-04 09:10:55.118513

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '829f639ffb10'
down_revision: Union[str, None] = '6360d085c2af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('review',
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('critic_id', sa.BigInteger(), nullable=False),
    sa.Column('book_id', sa.BigInteger(), nullable=False),
    sa.Column('rating', sa.Integer(), nullable=False),
    sa.Column('body', sa.String(), nullable=True),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['tenant.book.id'], ),
    sa.ForeignKeyConstraint(['critic_id'], ['tenant.critic.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('critic_id', 'book_id', name='uc_Review_CriticId_BookId'),
    # sa.UniqueConstraint('book_id', 'critic_id', name=op.f('uq_review_book_id')),
    schema='tenant',
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('review', schema='tenant')
    # ### end Alembic commands ###
