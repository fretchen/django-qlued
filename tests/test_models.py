"""
Test the models of this app.
"""

from datetime import datetime
import uuid

import pytz

from decouple import config
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

from qlued.models import Token, StorageProviderDb

User = get_user_model()


class TokenCreationTest(TestCase):
    """
    The test for token creation etc.
    """

    def setUp(self):
        self.username = config("USERNAME_TEST")
        self.password = config("PASSWORD_TEST")
        user = User.objects.create(username=self.username)
        user.set_password(self.password)
        user.save()
        self.user = user

    def test_token_creation(self):
        """
        Test that we can properly create tokens.
        """

        key = uuid.uuid4().hex
        token = Token.objects.create(
            key=key, user=self.user, created_at=datetime.now(pytz.utc), is_active=True
        )
        self.assertEqual(token.key, key)

        # make sure that we cannot create a second token with the same key
        with self.assertRaises(IntegrityError):
            _ = Token.objects.create(
                key=key,
                user=self.user,
                created_at=datetime.now(pytz.utc),
                is_active=True,
            )


class StorageProviderDbCreationTest(TestCase):
    """
    Test if it is possible to create a dropbox storage
    """

    def setUp(self):
        self.username = config("USERNAME_TEST")
        self.password = config("PASSWORD_TEST")
        user = User.objects.create(username=self.username)
        user.set_password(self.password)
        user.save()
        self.user = user

    def test_mongo_storage_db_creation(self):
        """
        Test that we can properly create a storage provide with mongodb.
        """
        mongodb_username = config("MONGODB_USERNAME")
        mongodb_password = config("MONGODB_PASSWORD")
        mongodb_database_url = config("MONGODB_DATABASE_URL")
        login_dict = {
            "mongodb_username": mongodb_username,
            "mongodb_password": mongodb_password,
            "mongodb_database_url": mongodb_database_url,
        }

        # create the storage entry in the models
        mongo_entry = StorageProviderDb.objects.create(
            storage_type="mongodb",
            name="mongodbtest",
            owner=self.user,
            description="MongoDB storage provider for tests",
            login=login_dict,
        )
        mongo_entry.full_clean()
        self.assertEqual(mongo_entry.owner, self.user)

        # make sure that we cannot some random storage type
        mongo_stupid = StorageProviderDb.objects.create(
            storage_type="mongodb_random",
            name="mongodbtest2",
            owner=self.user,
            description="MongoDB storage provider for tests",
            login=login_dict,
        )
        with self.assertRaises(ValidationError):
            mongo_stupid.full_clean()

        # make sure that the name cannot contain underscores
        mongo_stupid = StorageProviderDb.objects.create(
            storage_type="mongodb",
            name="mongodb_test_3",
            owner=self.user,
            description="MongoDB storage provider for tests",
            login=login_dict,
        )
        with self.assertRaises(ValidationError):
            mongo_stupid.full_clean()

        # make sure that the name cannot contain spaces
        mongo_stupid = StorageProviderDb.objects.create(
            storage_type="mongodb",
            name="mongodb test",
            owner=self.user,
            description="MongoDB storage provider for tests",
            login=login_dict,
        )
        with self.assertRaises(ValidationError):
            mongo_stupid.full_clean()

        # make sure that we cannot create a second storageprovide with the same name
        with self.assertRaises(IntegrityError):
            _ = StorageProviderDb.objects.create(
                storage_type="mongodb",
                name="mongodbtest",
                owner=self.user,
                description="MongoDB storage provider for tests",
                login=login_dict,
            )

    def test_drobox_creation(self):
        """
        Test that we can properly create a storage provide with Dropbox.
        """
        app_key = config("APP_KEY")
        app_secret = config("APP_SECRET")
        refresh_token = config("REFRESH_TOKEN")

        login_dict = {
            "app_key": app_key,
            "app_secret": app_secret,
            "refresh_token": refresh_token,
        }

        # create the storage entry in the models
        dropbox_entry = StorageProviderDb.objects.create(
            storage_type="dropbox",
            name="dropboxtest",
            owner=self.user,
            description="Dropbox storage provider for tests",
            login=login_dict,
        )
        dropbox_entry.full_clean()
        self.assertEqual(dropbox_entry.owner, self.user)

        # make sure that we cannot create a second storageprovide with the same name
        with self.assertRaises(IntegrityError):
            _ = StorageProviderDb.objects.create(
                storage_type="dropbox",
                name="dropboxtest",
                owner=self.user,
                description="Dropbox storage provider for tests",
                login=login_dict,
            )
