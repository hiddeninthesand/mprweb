import pytest

from sqlalchemy.exc import IntegrityError

from aurweb import db
from aurweb.models.package_base import PackageBase
from aurweb.models.package_blacklist import PackageBlacklist
from aurweb.models.user import User
from aurweb.testing import setup_test_db

user = pkgbase = None


@pytest.fixture(autouse=True)
def setup():
    global user, pkgbase

    setup_test_db("PackageBlacklist", "PackageBases", "Users")

    user = db.create(User, Username="test", Email="test@example.org",
                     RealName="Test User", Passwd="testPassword")
    pkgbase = db.create(PackageBase, Name="test-package", Maintainer=user)


def test_package_blacklist_creation():
    with db.begin():
        package_blacklist = db.create(PackageBlacklist, Name="evil-package")
    assert bool(package_blacklist.ID)
    assert package_blacklist.Name == "evil-package"


def test_package_blacklist_null_name_raises_exception():
    with pytest.raises(IntegrityError):
        with db.begin():
            db.create(PackageBlacklist)
    db.rollback()