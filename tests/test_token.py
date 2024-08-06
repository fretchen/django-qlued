"""
In this module, we make sure that the user can have the correct token as he tries to identify with his private key.
"""

import uuid

from decouple import config
from django.contrib.auth import get_user_model
from django.test import TestCase
from sqooler.schemes import LocalLoginInformation
from sqooler.security import create_jwk_pair
from sqooler.storage_providers.local import LocalProviderExtended as LocalProvider

from qlued.models import StorageProviderDb

User = get_user_model()


class UserTokenTests(TestCase):
    """
    The class that contains tests for the storage provider functions.
    """

    def setUp(self):
        # create a user
        self.username = config("USERNAME_TEST")
        self.password = config("PASSWORD_TEST")
        user = User.objects.create(username=self.username)
        user.set_password(self.password)
        user.save()

        # add the first storage provider
        base_path = "storage-3"

        login_dict = {
            "base_path": base_path,
        }

        local_entry = StorageProviderDb.objects.create(
            storage_type="local",
            name="local1",
            owner=user,
            description="First storage provider for tests",
            login=login_dict,
        )
        local_entry.full_clean()
        local_entry.save()

    def test_create_user_token(self) -> None:
        """
        Test that we can create a user token
        """
        entry = StorageProviderDb.objects.get(name="localtest")
        login_info = LocalLoginInformation(**entry.login)
        storage_provider = LocalProvider(login_info, entry.name)
        self.assertIsNotNone(storage_provider)

        private_jwk, public_jwk = create_jwk_pair(self.username)

        # the private key is for the user only and for signing jobs etc
        # now we need to create a uuid for the user, safe it and upload the token at the appropiate point.

        # the public key is there to identify the user
        storage_provider.upload_config(
            config_info, display_name=backend_name, private_jwk=private_jwk
        )
