"""add user

Revision ID: 84310a5c9e71
Revises: 20f444146781
Create Date: 2024-11-04 15:53:30.446979

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "84310a5c9e71"
down_revision: Union[str, None] = "20f444146781"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "apicallresponse",
        sa.Column("user", sa.String(length=100), nullable=True),
        schema="noshow",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("apicallresponse", "user", schema="noshow")
    # ### end Alembic commands ###
