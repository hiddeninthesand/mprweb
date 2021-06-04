from datetime import datetime

import pytest

from starlette.authentication import AuthenticationError

import aurweb.config

from aurweb.auth import BasicAuthBackend, has_credential
from aurweb.db import create, query
from aurweb.models.account_type import AccountType
from aurweb.models.session import Session
from aurweb.models.user import User
from aurweb.testing import setup_test_db
from aurweb.testing.requests import Request

user = backend = request = None


@pytest.fixture(autouse=True)
def setup():
    global user, backend, request

    setup_test_db("Users", "Sessions")

    account_type = query(AccountType,
                         AccountType.AccountType == "User").first()
    user = create(User, Username="test", Email="test@example.com",
                  RealName="Test User", Passwd="testPassword",
                  AccountType=account_type)

    backend = BasicAuthBackend()
    request = Request()


@pytest.mark.asyncio
async def test_auth_backend_missing_sid():
    # The request has no AURSID cookie, so authentication fails, and
    # AnonymousUser is returned.
    _, result = await backend.authenticate(request)
    assert not result.is_authenticated()


@pytest.mark.asyncio
async def test_auth_backend_invalid_sid():
    # Provide a fake AURSID that won't be found in the database.
    # This results in our path going down the invalid sid route,
    # which gives us an AnonymousUser.
    request.cookies["AURSID"] = "fake"
    _, result = await backend.authenticate(request)
    assert not result.is_authenticated()


@pytest.mark.asyncio
async def test_auth_backend_invalid_user_id():
    # Create a new session with a fake user id.
    now_ts = datetime.utcnow().timestamp()
    db_backend = aurweb.config.get("database", "backend")
    with pytest.raises(IntegrityError):
        create(Session, UsersID=666, SessionID="realSession",
               LastUpdateTS=now_ts + 5)

    session.rollback()


@pytest.mark.asyncio
async def test_basic_auth_backend():
    # This time, everything matches up. We expect the user to
    # equal the real_user.
    now_ts = datetime.utcnow().timestamp()
    create(Session, UsersID=user.ID, SessionID="realSession",
           LastUpdateTS=now_ts + 5)
    _, result = await backend.authenticate(request)
    assert result == user


def test_has_fake_credential_fails():
    # Fake credential 666 does not exist.
    assert not has_credential(user, 666)
