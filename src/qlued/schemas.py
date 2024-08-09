"""
The schemas that define our communication with the api.
"""

from ninja import Schema


# pylint: disable=R0903
class JobSchemaWithTokenIn(Schema):
    """
    The schema that is set up for the submission of new jobs.  This is the schema used in v2
    as it allows for token based authentification only.
    """

    job: str
    token: str
