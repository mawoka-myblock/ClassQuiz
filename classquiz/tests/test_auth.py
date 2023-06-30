# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import pytest
from classquiz.auth import get_password_hash, verify_password, settings, ALGORITHM, create_access_token
from jose import JWTError, jwt

test_passwords = ["password", "password123", "12345678", "saddsaasdsad", "dsadasasdasddasasdsdasad"]


@pytest.mark.asyncio
@pytest.mark.parametrize("password", test_passwords)
async def test_password_hashes(password):
    passwd_hash = get_password_hash(password)
    assert verify_password(password, passwd_hash)


@pytest.mark.asyncio
async def test_jwt_engine():
    access_token = create_access_token({"sub": "test@test.com"})
    assert access_token is not None
    payload = jwt.decode(access_token, settings.secret_key, algorithms=[ALGORITHM])
    email: str = payload.get("sub")
    assert email == "test@test.com"
    with pytest.raises(JWTError):
        jwt.decode(access_token, "wrong_secret", algorithms=[ALGORITHM])
