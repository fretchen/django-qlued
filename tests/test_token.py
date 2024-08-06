"""
In this module, we make sure that the user can have the correct token as he tries to identify with his private key.
"""

import shutil
import uuid
from datetime import datetime

import pytz
from decouple import config
from django.contrib.auth import get_user_model
from django.test import TestCase
from icecream import ic
from sqooler.schemes import LocalLoginInformation
from sqooler.security import create_jwk_pair
from sqooler.storage_providers.local import LocalProviderExtended as LocalProvider

from qlued.models import StorageProviderDb, Token

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
        self.user = user

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

    def tearDown(self):
        shutil.rmtree("storage-3", ignore_errors=True)

    def test_create_user_token(self) -> None:
        """
        Test that we can create a user token
        """
        entry = StorageProviderDb.objects.get(name="local1")
        login_info = LocalLoginInformation(**entry.login)
        storage_provider = LocalProvider(login_info, entry.name)
        self.assertIsNotNone(storage_provider)

        # now we need to create a uuid for the user, safe it and upload the token at the appropiate point.
        user_uuid = uuid.uuid4().hex[:24]
        user_kid = f"user{user_uuid}"

        private_jwk, public_jwk = create_jwk_pair(user_kid)
        ic(public_jwk)
        # the private key is for the user only and for signing jobs etc

        # now put it all together to upload a token for the user into the database
        token = Token.objects.create(
            key=public_jwk.x,
            user=self.user,
            created_at=datetime.now(pytz.utc),
            is_active=True,
            storage_provider=entry,
            uuid_hex=user_uuid,
        )

        self.assertEqual(token.key, public_jwk.x)

        # now that the token is in the database we also upload the appropiate public_key to the
        # storage_provider
        storage_provider.upload_public_key(
            public_jwk, display_name=self.username, role="user"
        )

        # clean up the token
        token.delete()
        self.assertEqual(Token.objects.filter(key=public_jwk.x).count(), 0)

        # and also remove it from the storage_provider
        storage_provider._delete_public_key(f"user{user_uuid}")
