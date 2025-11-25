import pytest
from unittest.mock import patch, MagicMock
from app.auth import jwt as jwt_module
from app.schemas.token import TokenType

def test_create_token_error(monkeypatch):
    monkeypatch.setattr(jwt_module, "jwt", MagicMock(encode=MagicMock(side_effect=Exception("fail"))))
    with pytest.raises(Exception):
        jwt_module.create_token("user", TokenType.ACCESS)

def test_decode_token_invalid_type(monkeypatch):
    async def fake_is_blacklisted(jti): return False
    monkeypatch.setattr(jwt_module, "is_blacklisted", fake_is_blacklisted)
    token = jwt_module.create_token("user", TokenType.ACCESS)
    with pytest.raises(Exception):
        import asyncio
        payload = asyncio.run(jwt_module.decode_token(token, TokenType.REFRESH))

def test_decode_token_revoked(monkeypatch):
    async def fake_is_blacklisted(jti): return True
    monkeypatch.setattr(jwt_module, "is_blacklisted", fake_is_blacklisted)
    token = jwt_module.create_token("user", TokenType.ACCESS)
    with pytest.raises(Exception):
        import asyncio
        payload = asyncio.run(jwt_module.decode_token(token, TokenType.ACCESS))

def test_decode_token_expired(monkeypatch):
    import time
    token = jwt_module.create_token("user", TokenType.ACCESS, expires_delta=None)
    # Patch jwt.decode to raise ExpiredSignatureError
    class ExpiredSignatureError(Exception): pass
    monkeypatch.setattr(jwt_module.jwt, "decode", MagicMock(side_effect=ExpiredSignatureError))
    with pytest.raises(Exception):
        import asyncio
        payload = asyncio.run(jwt_module.decode_token(token, TokenType.ACCESS))

def test_decode_token_jwt_error(monkeypatch):
    class JWTError(Exception): pass
    monkeypatch.setattr(jwt_module.jwt, "decode", MagicMock(side_effect=JWTError))
    with pytest.raises(Exception):
        import asyncio
        payload = asyncio.run(jwt_module.decode_token("token", TokenType.ACCESS))

def test_get_current_user_exceptions(monkeypatch):
    async def fake_decode_token(token, token_type): return {"sub": "bad"}
    monkeypatch.setattr(jwt_module, "decode_token", fake_decode_token)
    db = MagicMock()
    db.query().filter().first.return_value = None
    with pytest.raises(Exception):
        import asyncio
        asyncio.run(jwt_module.get_current_user(token="token", db=db))
    db.query().filter().first.return_value = MagicMock(is_active=False)
    with pytest.raises(Exception):
        import asyncio
        asyncio.run(jwt_module.get_current_user(token="token", db=db))
