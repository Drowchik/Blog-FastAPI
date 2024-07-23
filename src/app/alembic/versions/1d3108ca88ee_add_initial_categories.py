"""add initial categories

Revision ID: 1d3108ca88ee
Revises: e6fb6e1a8803
Create Date: 2024-07-14 15:38:23.734591

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d3108ca88ee'
down_revision: Union[str, None] = 'e6fb6e1a8803'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("INSERT INTO categories (name) VALUES ('Technology')")
    op.execute("INSERT INTO categories (name) VALUES ('Science')")
    op.execute("INSERT INTO categories (name) VALUES ('Art')")


def downgrade() -> None:
   op.execute("DELETE FROM categories WHERE name IN ('Technology', 'Science', 'Art')")
