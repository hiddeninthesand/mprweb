"""Added ApiKeys table

Revision ID: 8815353c32e5
Revises: 5fe6830206a3
Create Date: 2022-03-21 22:38:23.404104

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "8815353c32e5"
down_revision = "5fe6830206a3"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "ApiKeys",
        sa.Column("ID", mysql.INTEGER(unsigned=True), nullable=False),
        sa.Column("UserID", mysql.INTEGER(unsigned=True), nullable=False),
        sa.Column("Key", sa.Text(), nullable=False),
        sa.Column("Note", sa.Text(), server_default=sa.text("''"), nullable=True),
        sa.Column("ExpireTS", mysql.BIGINT(unsigned=True), nullable=True),
        sa.ForeignKeyConstraint(["UserID"], ["Users.ID"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("ID"),
        sa.UniqueConstraint("Key"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )
    op.alter_column(
        "PackageKeywords",
        "PackageBaseID",
        existing_type=mysql.INTEGER(display_width=10, unsigned=True),
        nullable=True,
    )
    op.alter_column(
        "PackageLicenses",
        "PackageID",
        existing_type=mysql.INTEGER(display_width=10, unsigned=True),
        nullable=True,
    )
    op.alter_column(
        "PackageLicenses",
        "LicenseID",
        existing_type=mysql.INTEGER(display_width=10, unsigned=True),
        nullable=True,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "PackageLicenses",
        "LicenseID",
        existing_type=mysql.INTEGER(display_width=10, unsigned=True),
        nullable=False,
    )
    op.alter_column(
        "PackageLicenses",
        "PackageID",
        existing_type=mysql.INTEGER(display_width=10, unsigned=True),
        nullable=False,
    )
    op.alter_column(
        "PackageKeywords",
        "PackageBaseID",
        existing_type=mysql.INTEGER(display_width=10, unsigned=True),
        nullable=False,
    )
    op.drop_table("ApiKeys")
    # ### end Alembic commands ###