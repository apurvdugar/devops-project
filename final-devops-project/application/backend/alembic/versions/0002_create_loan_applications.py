from alembic import op
import sqlalchemy as sa

revision = "0002_create_loan_applications"
down_revision = "0001_create_tasks"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "loan_applications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("applicant_name", sa.String(length=200), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("loan_type", sa.String(length=20), nullable=False),
        sa.Column("principal_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("annual_interest_rate", sa.Numeric(5, 2), nullable=False),
        sa.Column("tenure_months", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="submitted"),
        sa.Column("emi", sa.Numeric(12, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.drop_table("tasks")


def downgrade():
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("priority", sa.String(length=20), nullable=False, server_default="MEDIUM"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="TODO"),
        sa.Column("assignee", sa.String(length=120), nullable=False, server_default="Unassigned"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.drop_table("loan_applications")
