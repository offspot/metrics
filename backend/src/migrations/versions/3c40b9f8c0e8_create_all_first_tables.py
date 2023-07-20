"""Create all first tables

Revision ID: 3c40b9f8c0e8
Revises: 
Create Date: 2023-06-22 15:31:27.659225

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3c40b9f8c0e8"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "indicator_dimension",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("value0", sa.String(), nullable=True),
        sa.Column("value1", sa.String(), nullable=True),
        sa.Column("value2", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_indicator_dimension")),
    )
    op.create_index(
        op.f("ix_indicator_dimension_value0"),
        "indicator_dimension",
        ["value0"],
        unique=False,
    )
    op.create_table(
        "indicator_period",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("day", sa.Integer(), nullable=False),
        sa.Column("weekday", sa.Integer(), nullable=False),
        sa.Column("hour", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_indicator_period")),
        sa.UniqueConstraint(
            "year", "month", "day", "hour", name=op.f("uq_indicator_period_year")
        ),
    )
    op.create_table(
        "kpi",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("kpi_id", sa.Integer(), nullable=False),
        sa.Column("agg_kind", sa.String(), nullable=False),
        sa.Column("agg_value", sa.String(), nullable=False),
        sa.Column("kpi_value", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_kpi")),
        sa.UniqueConstraint("kpi_id", "agg_value", name=op.f("uq_kpi_kpi_id")),
    )
    op.create_index(op.f("ix_kpi_kpi_id"), "kpi", ["kpi_id"], unique=False)
    op.create_index("kpi_id", "kpi", ["agg_kind"], unique=False)
    op.create_table(
        "indicator_record",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("indicator_id", sa.Integer(), nullable=False),
        sa.Column("value", sa.Integer(), nullable=False),
        sa.Column("period_id", sa.Integer(), nullable=False),
        sa.Column("dimension_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["dimension_id"],
            ["indicator_dimension.id"],
            name=op.f("fk_indicator_record_dimension_id_indicator_dimension"),
        ),
        sa.ForeignKeyConstraint(
            ["period_id"],
            ["indicator_period.id"],
            name=op.f("fk_indicator_record_period_id_indicator_period"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_indicator_record")),
        sa.UniqueConstraint(
            "indicator_id",
            "period_id",
            "dimension_id",
            name=op.f("uq_indicator_record_indicator_id"),
        ),
    )
    op.create_index(
        op.f("ix_indicator_record_indicator_id"),
        "indicator_record",
        ["indicator_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_indicator_record_period_id"),
        "indicator_record",
        ["period_id"],
        unique=False,
    )
    op.create_table(
        "indicator_state",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("indicator_id", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(), nullable=False),
        sa.Column("period_id", sa.Integer(), nullable=False),
        sa.Column("dimension_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["dimension_id"],
            ["indicator_dimension.id"],
            name=op.f("fk_indicator_state_dimension_id_indicator_dimension"),
        ),
        sa.ForeignKeyConstraint(
            ["period_id"],
            ["indicator_period.id"],
            name=op.f("fk_indicator_state_period_id_indicator_period"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_indicator_state")),
        sa.UniqueConstraint(
            "indicator_id",
            "period_id",
            "dimension_id",
            name=op.f("uq_indicator_state_indicator_id"),
        ),
    )
    op.create_index(
        op.f("ix_indicator_state_indicator_id"),
        "indicator_state",
        ["indicator_id"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_indicator_state_indicator_id"), table_name="indicator_state")
    op.drop_table("indicator_state")
    op.drop_index(op.f("ix_indicator_record_period_id"), table_name="indicator_record")
    op.drop_index(
        op.f("ix_indicator_record_indicator_id"), table_name="indicator_record"
    )
    op.drop_table("indicator_record")
    op.drop_index("kpi_id", table_name="kpi")
    op.drop_index(op.f("ix_kpi_kpi_id"), table_name="kpi")
    op.drop_table("kpi")
    op.drop_table("indicator_period")
    op.drop_index(
        op.f("ix_indicator_dimension_value0"), table_name="indicator_dimension"
    )
    op.drop_table("indicator_dimension")
    # ### end Alembic commands ###