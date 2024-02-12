"""
The tests for the main storage_provider functions
"""

import shutil

from decouple import config

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.db import IntegrityError

from sqooler.storage_providers.local import LocalProviderExtended as LocalProvider
from sqooler.schemes import LocalLoginInformation, BackendConfigSchemaIn

from django.core.exceptions import ValidationError as DjangoValidationError

from pydantic import ValidationError as PydancticValidationError

from qlued.models import StorageProviderDb

from qlued.storage_providers import (
    get_storage_provider,
    get_storage_provider_from_entry,
)

User = get_user_model()


class StorageProvideTests(TestCase):
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

        # create a dummy config for the required fermions
        backend_name = "fermions"
        fermions_config = {
            "display_name": "fermions",
            "name": "alqor_fermionic-tweezer_simulator",
            "supported_instructions": [],
            "wire_order": "interleaved",
            "gates": [],
            "simulator": True,
            "num_wires": 2,
            "num_species": 1,
            "version": "0.0.1",
            "max_shots": 100,
            "max_experiments": 100,
            "cold_atom_type": "fermions",
            "description": "First device for tests",
            "operational": True,
        }

        local_storage = get_storage_provider_from_entry(local_entry)
        config_info = BackendConfigSchemaIn(**fermions_config)
        local_storage.upload_config(config_info, backend_name)

        # add the second storage provider
        base_path = "storage-4"

        login_dict = {
            "base_path": base_path,
        }

        local_entry = StorageProviderDb.objects.create(
            storage_type="local",
            name="local2",
            owner=user,
            description="Second storage provider for tests",
            login=login_dict,
        )
        local_entry.full_clean()
        local_entry.save()

        # create a dummy config for the required single qudit

        backend_name = "singlequdit"
        single_qudit_config = {
            "display_name": "singlequdit",
            "gates": [],
            "supported_instructions": [],
            "simulator": True,
            "num_wires": 1,
            "wire_order": "interleaved",
            "num_species": 1,
            "version": "0.0.1",
            "max_shots": 100,
            "max_experiments": 100,
            "cold_atom_type": "fermions",
            "description": "Second device for tests",
            "operational": True,
        }

        local_storage = get_storage_provider_from_entry(local_entry)
        config_info = BackendConfigSchemaIn(**single_qudit_config)
        local_storage.upload_config(config_info, backend_name)

    def tearDown(self):
        shutil.rmtree("storage-3")
        shutil.rmtree("storage-4")

    def test_get_storage_provider_from_entry(self):
        """
        Test the get_storage_provider function
        """
        # first get the entry
        db_entry = StorageProviderDb.objects.get(name="local2")

        login_info = LocalLoginInformation(**db_entry.login)
        storage_provider = LocalProvider(login_info, db_entry.name)

        # test if the storage provider is having the correct name
        self.assertEqual(storage_provider.name, "local2")

        # try to get the storage provider from the entry
        backend_name = "singlequdit"

        # make sure that this raises the does not exist error
        with self.assertRaises(StorageProviderDb.DoesNotExist):
            get_storage_provider(backend_name)

        full_backend_name = "local2_singlequdit_simulator"
        storage_provider = get_storage_provider(full_backend_name)

    def test_add_local_provider(self):
        """
        Test that we can add a local provider
        """
        # create the storage entry in the models with a poor login dict
        poor_login_dict = {
            "app_key_t": "test",
            "app_secret": "test",
            "refresh_token": "test",
        }
        local_entry = StorageProviderDb.objects.create(
            storage_type="local",
            name="localtest342",
            owner=self.user,
            description="Local storage provider for tests",
            login=poor_login_dict,
            is_active=True,
        )
        with self.assertRaises(DjangoValidationError):
            local_entry.full_clean()

        local_entry.delete()

        # create the storage entry in the models
        login_dict = {"base_path": "test"}
        local_entry = StorageProviderDb.objects.create(
            storage_type="local",
            name="localtest342",
            owner=self.user,
            description="Local storage provider for tests",
            login=login_dict,
            is_active=True,
        )

        local_entry.full_clean()

        # make sure that the name is unique
        with self.assertRaises(IntegrityError):
            StorageProviderDb.objects.create(
                storage_type="local",
                name="localtest342",
                owner=self.user,
                description="Local storage provider for tests",
                login=login_dict,
                is_active=True,
            )

    def test_add_mongodb_provider(self):
        """
        Test that we can add a MongoDB provider
        """
        # create the storage entry in the models with a poor login dict
        poor_login_dict = {
            "app_key_t": "test",
            "app_secret": "test",
            "refresh_token": "test",
        }
        local_entry = StorageProviderDb.objects.create(
            storage_type="mongodb",
            name="localtest342",
            owner=self.user,
            description="Local storage provider for tests",
            login=poor_login_dict,
            is_active=True,
        )
        with self.assertRaises(DjangoValidationError):
            local_entry.full_clean()

        local_entry.delete()

        # create the storage entry in the models
        login_dict = {
            "mongodb_database_url": "test",
            "mongodb_username": "test",
            "mongodb_password": "test",
        }
        local_entry = StorageProviderDb.objects.create(
            storage_type="mongodb",
            name="localtest342",
            owner=self.user,
            description="Local storage provider for tests",
            login=login_dict,
            is_active=True,
        )

        local_entry.full_clean()

        # make sure that the name is unique
        with self.assertRaises(IntegrityError):
            StorageProviderDb.objects.create(
                storage_type="mongodb",
                name="localtest342",
                owner=self.user,
                description="Local storage provider for tests",
                login=login_dict,
                is_active=True,
            )
