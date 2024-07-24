"""Add created_at column to dispatches

Revision ID: 9c169442039e
Revises: d16598f356c1
Create Date: 2024-07-23 19:09:50.482747

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9c169442039e'
down_revision: Union[str, None] = 'd16598f356c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
