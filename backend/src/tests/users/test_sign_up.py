from typing import cast

import pytest
from fastapi import HTTPException
from models.users import UserSQL
from sqlalchemy import select
from use_cases.users.create_user import CreateUserRequest, CreateUserResponse

DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.mark.asyncio
async def test_sign_up(test_app, db_session):
    app, injector, pydiator = test_app
    response = cast(
        CreateUserResponse,
        await pydiator.send(
            req=CreateUserRequest(
                email="test+1@gmail.com",
                first_name="Test",
                last_name="Test",
                password="String1234",
                r_password="String1234",
            )
        ),
    )
    user = await db_session.scalar(
        select(UserSQL).where(UserSQL.email == "test+1@gmail.com")
    )
    assert response.user.id == user.id


@pytest.mark.asyncio
async def test_user_is_exist(test_app, user_fixture):
    _, _, pydiator = test_app
    is_exist = False
    try:
        await pydiator.send(
            req=CreateUserRequest(
                email=user_fixture.email,
                first_name="Test",
                last_name="Test",
                password="String1234",
                r_password="String1234",
            )
        )
    except HTTPException:
        is_exist = True
    assert is_exist is True


@pytest.mark.asyncio
async def test_user_tree(test_app, user_fixture):
    assert 1 == 1
