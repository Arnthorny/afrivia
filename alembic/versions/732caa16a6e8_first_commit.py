"""First commit

Revision ID: 732caa16a6e8
Revises: 
Create Date: 2024-09-04 02:51:37.241715

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '732caa16a6e8'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categories',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('countries',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('moderators',
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('mod_country_preferences',
    sa.Column('moderator_id', sa.String(), nullable=False),
    sa.Column('country_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['country_id'], ['countries.id'], ),
    sa.ForeignKeyConstraint(['moderator_id'], ['moderators.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('moderator_id', 'country_id')
    )
    op.create_table('submissions',
    sa.Column('question', sa.Text(), nullable=False),
    sa.Column('status', sa.Enum('pending', 'approved', 'rejected', name='submissionstatusenum'), nullable=False),
    sa.Column('moderator_id', sa.String(), nullable=False),
    sa.Column('difficulty', sa.Enum('easy', 'medium', 'hard', name='difficultyenum'), nullable=False),
    sa.Column('submission_note', sa.Text(), nullable=True),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['moderator_id'], ['moderators.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('question')
    )
    op.create_table('categories_submissions',
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('submission_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.ForeignKeyConstraint(['submission_id'], ['submissions.id'], ),
    sa.PrimaryKeyConstraint('category_id', 'submission_id')
    )
    op.create_table('countries_submissions',
    sa.Column('country_id', sa.Integer(), nullable=False),
    sa.Column('submission_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['country_id'], ['countries.id'], ),
    sa.ForeignKeyConstraint(['submission_id'], ['submissions.id'], ),
    sa.PrimaryKeyConstraint('country_id', 'submission_id')
    )
    op.create_table('submission_options',
    sa.Column('submission_id', sa.String(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('is_correct', sa.Boolean(), nullable=False),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['submission_id'], ['submissions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('trivias',
    sa.Column('question', sa.Text(), nullable=False),
    sa.Column('difficulty', sa.Enum('easy', 'medium', 'hard', name='difficultyenum'), nullable=False),
    sa.Column('submission_id', sa.String(), nullable=True),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['submission_id'], ['submissions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('categories_trivias',
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('trivia_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.ForeignKeyConstraint(['trivia_id'], ['trivias.id'], ),
    sa.PrimaryKeyConstraint('category_id', 'trivia_id')
    )
    op.create_table('countries_trivias',
    sa.Column('country_id', sa.Integer(), nullable=False),
    sa.Column('trivia_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['country_id'], ['countries.id'], ),
    sa.ForeignKeyConstraint(['trivia_id'], ['trivias.id'], ),
    sa.PrimaryKeyConstraint('country_id', 'trivia_id')
    )
    op.create_table('trivia_options',
    sa.Column('trivia_id', sa.String(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('is_correct', sa.Boolean(), nullable=False),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['trivia_id'], ['trivias.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('trivia_options')
    op.drop_table('countries_trivias')
    op.drop_table('categories_trivias')
    op.drop_table('trivias')
    op.drop_table('submission_options')
    op.drop_table('countries_submissions')
    op.drop_table('categories_submissions')
    op.drop_table('submissions')
    op.drop_table('mod_country_preferences')
    op.drop_table('moderators')
    op.drop_table('countries')
    op.drop_table('categories')
    # ### end Alembic commands ###
