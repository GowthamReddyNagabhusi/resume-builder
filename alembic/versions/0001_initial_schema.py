"""initial_schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-03-11
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Schema is managed in backend/database/models.py init_db for this SQLite project.
    pass


def downgrade() -> None:
    pass
