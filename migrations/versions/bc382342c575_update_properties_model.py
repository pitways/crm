"""Update Properties model

Revision ID: bc382342c575
Revises: 
Create Date: 2023-02-24 21:35:32.122520

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'bc382342c575'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password', sa.String(length=128), nullable=False))
        batch_op.add_column(sa.Column('username', sa.String(length=255), nullable=False))
        batch_op.add_column(sa.Column('is_admin', sa.Boolean(), nullable=True))
        batch_op.alter_column('email',
                              existing_type=sa.VARCHAR(length=50),
                              type_=sa.String(length=255),
                              existing_nullable=False)
        batch_op.create_unique_constraint(None, ['email'])
        batch_op.drop_column('name')
        batch_op.drop_column('marital_status')
        batch_op.drop_column('income')
        batch_op.drop_column('profession')
        batch_op.drop_column('address')
        batch_op.drop_column('phone')
        batch_op.drop_column('birthdate')

    with op.batch_alter_table('properties', schema=None) as batch_op:
        batch_op.alter_column('photo',
                              existing_type=sa.VARCHAR(length=200),
                              type_=sa.LargeBinary(),
                              nullable=True)

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('password',
                              existing_type=sa.VARCHAR(length=255),
                              type_=sa.String(length=128),
                              existing_nullable=False)
        batch_op.drop_column('password_hash')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password_hash', sa.VARCHAR(length=128), nullable=True))
        batch_op.alter_column('password',
                              existing_type=sa.String(length=128),
                              type_=sa.VARCHAR(length=255),
                              existing_nullable=False)

    with op.batch_alter_table('properties', schema=None) as batch_op:
        batch_op.alter_column('photo',
                              existing_type=sa.LargeBinary(),
                              type_=sa.VARCHAR(length=200),
                              nullable=False)

    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.add_column(sa.Column('birthdate', sa.VARCHAR(length=20), nullable=True))
        batch_op.add_column(sa.Column('phone', sa.VARCHAR(length=20), nullable=True))
        batch_op.add_column(sa.Column('address', sa.VARCHAR(length=200), nullable=True))
        batch_op.add_column(sa.Column('profession', sa.VARCHAR(length=50), nullable=True))
        batch_op.add_column(sa.Column('income', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('marital_status', sa.VARCHAR(length=20), nullable=True))
        batch_op.add_column(sa.Column('name', sa.VARCHAR(length=50), nullable=False))
        batch_op.drop_constraint(None, type_='unique')
        batch_op.alter_column('email',
                              existing_type=sa.String(length=255),
                              type_=sa.VARCHAR(length=50),
                              existing_nullable=False)
        batch_op.drop_column('is_admin')
        batch_op.drop_column('username')
        batch_op.drop_column('password')

    # ### end Alembic commands ###