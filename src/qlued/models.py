"""
The models that define our sql tables for the app.
"""

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


class Token(models.Model):
    """
    The backend class for the tokens that allow access to the different backends etc.

    Args:
        key: CharField, contains authorization token value.
        user: ForeignKey, foreign key to the logged user.
        created_at: DateTimeField, contains date and time of token creation.
        is_active: BooleanField contains if token is active.
    """

    key = models.CharField(max_length=40, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField()
    is_active = models.BooleanField(default=False)


class StorageProviderDb(models.Model):
    """
    This class allows users to access storage providers in the same way as they
    would access other systems. So it contains all the necessary information to access
    the storage provider and open a connection.

    Args:
        storage_type: The type of storage provider.
        name: The name of the storage provider. Has to be unique.
        is_active: Is the storage provider active.
        owner: Which user owns this storage provider.
        description: An optional description of the storage provider.
        login: The login information for the storage provider.
    """

    STORAGE_TYPE_CHOICES = (
        ("dropbox", "Dropbox"),
        ("mongodb", "MongoDB"),
        ("local", "Local"),
    )

    # the storage_type. It can be "dropbox" or "mongodb".
    storage_type = models.CharField(
        max_length=20,
        choices=STORAGE_TYPE_CHOICES,
    )

    # the name of the storage provider. Has to be unique.
    name = models.CharField(max_length=50, unique=True)

    # is the storage provider active.
    is_active = models.BooleanField(default=True)

    # the owner of the storage provider.
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    # an optional description of the storage provider.
    description = models.CharField(max_length=500, null=True)

    # the login information for the storage provider. This is a json string.
    login = models.JSONField()

    def clean(self):
        if self.storage_type not in dict(self.STORAGE_TYPE_CHOICES):
            raise ValidationError(
                {"storage_type": f"Value '{self.storage_type}' is not a valid choice."}
            )
        # make sure that the name does not contain any spaces or underscores.
        if " " in self.name or "_" in self.name:
            raise ValidationError(
                {
                    "name": "The name of the storage provider cannot contain spaces or underscores."
                }
            )
