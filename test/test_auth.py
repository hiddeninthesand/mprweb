from datetime import datetime

import pytest

from sqlalchemy.exc import IntegrityError

from aurweb import db
from aurweb.auth import AnonymousUser, BasicAuthBackend, account_type_required, has_credential
from aurweb.models.account_type import USER, USER_ID
from aurweb.models.session import Session
from aurweb.models.user import User
from aurweb.testing.requests import Request

user = backend = request = None


@pytest.fixture(autouse=True)
def setup(db_test):
    global user, backend, request

    with db.begin():
        user = db.create(User, Username="test", Email="test@example.com",
                         RealName="Test User", Passwd="testPassword",
                         AccountTypeID=USER_ID)

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
    with pytest.raises(IntegrityError):
        Session(UsersID=666, SessionID="realSession",
                LastUpdateTS=now_ts + 5)


@pytest.mark.asyncio
async def test_basic_auth_backend():
    # This time, everything matches up. We expect the user to
    # equal the real_user.
    now_ts = datetime.utcnow().timestamp()
    with db.begin():
        db.create(Session, UsersID=user.ID, SessionID="realSession",
                  LastUpdateTS=now_ts + 5)
    request.cookies["AURSID"] = "realSession"
    _, result = await backend.authenticate(request)
    assert result == user


def test_has_fake_credential_fails():
    # Fake credential 666 does not exist.
    assert not has_credential(user, 666)


def test_account_type_required():
    """ This test merely asserts that a few different paths
    do not raise exceptions. """
    # This one shouldn't raise.
    account_type_required({USER})

    # This one also shouldn't raise.
    account_type_required({USER_ID})

    # But this one should! We have no "FAKE" key.
    with pytest.raises(KeyError):
        account_type_required({'FAKE'})


def test_is_trusted_user():
    user_ = AnonymousUser()
    assert not user_.is_trusted_user()


def test_is_developer():
    user_ = AnonymousUser()
    assert not user_.is_developer()


def test_is_elevated():
    user_ = AnonymousUser()
    assert not user_.is_elevated()


def test_voted_for():
    user_ = AnonymousUser()
    assert not user_.voted_for(None)


def test_notified():
    user_ = AnonymousUser()
    assert not user_.notified(None)


def test_has_credential():
    user_ = AnonymousUser()
    assert not user_.has_credential("FAKE_CREDENTIAL")
