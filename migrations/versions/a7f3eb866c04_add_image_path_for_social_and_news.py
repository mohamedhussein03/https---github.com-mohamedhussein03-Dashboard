"""add image_path for social and news

Revision ID: a7f3eb866c04
Revises: 1d770c6042fe
Create Date: 2026-01-20 20:34:23.311948

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7f3eb866c04'
down_revision = '1d770c6042fe'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("social_item") as batch_op:
        batch_op.add_column(
            sa.Column("image_path", sa.String(length=300), nullable=True)
        )
        batch_op.add_column(
            sa.Column("updated_at", sa.DateTime(), nullable=True)
        )
        batch_op.drop_column("image_url")

    with op.batch_alter_table("news_item") as batch_op:
        batch_op.add_column(
            sa.Column("image_path", sa.String(length=300), nullable=True)
        )
        batch_op.add_column(
            sa.Column("updated_at", sa.DateTime(), nullable=True)
        )


    # ### end Alembic commands ###


def downgrade():
    with op.batch_alter_table("social_item") as batch_op:
        batch_op.add_column(
            sa.Column("image_url", sa.String(length=300), nullable=True)
        )
        batch_op.drop_column("image_path")
        batch_op.drop_column("updated_at")

    with op.batch_alter_table("news_item") as batch_op:
        batch_op.drop_column("image_path")
        batch_op.drop_column("updated_at")


    # ### end Alembic commands ###
