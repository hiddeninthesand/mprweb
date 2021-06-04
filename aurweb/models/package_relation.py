from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import mapper

from aurweb.db import make_relationship
from aurweb.models.package import Package
from aurweb.models.relation_type import RelationType
from aurweb.schema import PackageRelations


class PackageRelation:
    def __init__(self, Package: Package = None,
                 RelationType: RelationType = None,
                 RelName: str = None, RelCondition: str = None,
                 RelArch: str = None):
        self.Package = Package
        if not self.Package:
            raise IntegrityError(
                statement="Foreign key PackageID cannot be null.",
                orig="PackageRelations.PackageID",
                params=("NULL"))

        self.RelationType = RelationType
        if not self.RelationType:
            raise IntegrityError(
                statement="Foreign key RelTypeID cannot be null.",
                orig="PackageRelations.RelTypeID",
                params=("NULL"))

        self.RelName = RelName  # nullable=False
        if not self.RelName:
            raise IntegrityError(
                statement="Column RelName cannot be null.",
                orig="PackageRelations.RelName",
                params=("NULL"))

        self.RelCondition = RelCondition
        self.RelArch = RelArch


properties = {
    "Package": make_relationship(Package, PackageRelations.c.PackageID,
                                 "package_relations"),
    "RelationType": make_relationship(RelationType,
                                      PackageRelations.c.RelTypeID,
                                      "package_relations")
}

mapper(PackageRelation, PackageRelations, properties=properties,
       primary_key=[
           PackageRelations.c.PackageID,
           PackageRelations.c.RelTypeID
       ])
