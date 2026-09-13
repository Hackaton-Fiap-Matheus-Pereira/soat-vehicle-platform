"""initial schema for both services"""
from alembic import context, op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    service = context.get_x_argument(as_dictionary=True).get("service", "vehicle_service")
    if service == "auth_service":
        op.create_table("users", sa.Column("id", sa.String(36), primary_key=True), sa.Column("name", sa.String(120), nullable=False), sa.Column("email", sa.String(255), nullable=False), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("role", sa.Enum("buyer", "admin", name="role"), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("email"))
        op.create_index("ix_users_email", "users", ["email"])
    else:
        op.create_table("vehicles", sa.Column("id", sa.String(36), primary_key=True), sa.Column("brand", sa.String(80), nullable=False), sa.Column("model", sa.String(120), nullable=False), sa.Column("year", sa.Integer(), nullable=False), sa.Column("color", sa.String(50), nullable=False), sa.Column("price", sa.Numeric(12, 2), nullable=False), sa.Column("status", sa.Enum("available", "sold", name="vehiclestatus"), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
        op.create_index("ix_vehicles_brand", "vehicles", ["brand"])
        op.create_index("ix_vehicles_model", "vehicles", ["model"])
        op.create_index("ix_vehicles_price", "vehicles", ["price"])
        op.create_table("sales", sa.Column("id", sa.String(36), primary_key=True), sa.Column("vehicle_id", sa.String(36), sa.ForeignKey("vehicles.id"), nullable=False), sa.Column("buyer_id", sa.String(36), nullable=False), sa.Column("sale_price", sa.Numeric(12, 2), nullable=False), sa.Column("sold_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("vehicle_id", name="uq_sale_vehicle"))
        op.create_index("ix_sales_buyer_id", "sales", ["buyer_id"])


def downgrade():
    service = context.get_x_argument(as_dictionary=True).get("service", "vehicle_service")
    if service == "auth_service":
        op.drop_table("users")
    else:
        op.drop_table("sales")
        op.drop_table("vehicles")

