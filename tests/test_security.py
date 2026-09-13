from types import SimpleNamespace

import jwt

from auth_service.models import Role
from auth_service.security import create_token, hash_password, verify_password


def test_password_is_hashed_and_verified():
    hashed = hash_password("StrongPass123!")
    assert hashed != "StrongPass123!"
    assert verify_password("StrongPass123!", hashed)
    assert not verify_password("wrong-password", hashed)


def test_token_contains_only_identity_claims():
    user = SimpleNamespace(id="buyer-123", role=Role.buyer, email="buyer@example.com")
    token = create_token(user)
    payload = jwt.decode(token, "test-secret-with-at-least-32-characters", algorithms=["HS256"], issuer="soat-auth-service")
    assert payload["sub"] == "buyer-123"
    assert payload["role"] == "buyer"
    assert "password" not in payload

