from typing import cast

import pytest
from fastapi import HTTPException
from use_cases.users.user_login import UserLoginRequest, UserLoginResponse


@pytest.mark.asyncio
async def test_user_succes_login(test_app, user_fixture):
    _, _, pydiator = test_app
    responce = cast(
        UserLoginResponse,
        await pydiator.send(
            req=UserLoginRequest(
                email=str(user_fixture.email),
                password="String1234",
            )
        ),
    )
    assert responce.user.email == user_fixture.email


@pytest.mark.asyncio
async def test_user_wrong_email(test_app, user_fixture):
    _, _, pydiator = test_app
    is_error = False
    try:
        await pydiator.send(
            req=UserLoginRequest(
                email="test+2@gmail.com",
                password="String1234",
            )
        )
    except HTTPException:
        is_error = True
    assert is_error is True


@pytest.mark.asyncio
async def test_user_wrong_password(test_app, user_fixture):
    _, _, pydiator = test_app
    is_error = False
    try:
        await pydiator.send(
            req=UserLoginRequest(
                email=str(user_fixture.email),
                password="String",
            )
        )
    except HTTPException:
        is_error = True
    assert is_error is True
