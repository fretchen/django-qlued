"""
In this module we test the API locally without the need of an external mongodb database.
"""

import json
import shutil

from decouple import config
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse_lazy
from icecream import ic
from sqooler.utils import get_dummy_config

from qlued.models import StorageProviderDb
from qlued.storage_providers import get_storage_provider_from_entry

from .utils import get_dummy_config

User = get_user_model()


class BackendConfigTest(TestCase):
    """
    The class that contains all the tests for this backends app.
    """

    def setUp(self):
        self.username = config("USERNAME_TEST")
        self.password = config("PASSWORD_TEST")
        user = User.objects.create(username=self.username)
        user.set_password(self.password)
        user.save()

        # put together the login information
        base_path = "storage"

        login_dict = {
            "base_path": base_path,
        }

        # create the storage entry in the models
        local_entry = StorageProviderDb.objects.create(
            storage_type="local",
            name="localtest",
            owner=user,
            description="Local storage provider for tests",
            login=login_dict,
            is_active=True,
        )
        local_entry.full_clean()
        local_entry.save()

    def tearDown(self):
        shutil.rmtree("storage")

    def test_get_backend_config(self):
        """
        Test that we can nicely and add remove the backend config.
        """
        backend_name, backend_info = get_dummy_config(sign=False)

        local_entry = StorageProviderDb.objects.get(name="localtest")

        local_storage = get_storage_provider_from_entry(local_entry)
        local_storage.upload_config(backend_info, backend_name)

        # test if the backend is now supposed to be operational.
        new_config_dict = local_storage.get_config(backend_name)

        assert "operational" not in new_config_dict

        # now look for the status
        backend_status = local_storage.get_backend_status(backend_name)

        assert backend_status.operational is False

        # now test that the backend status is obtained through the API
        url = reverse_lazy(
            "api-2.0.0:get_backend_status",
            kwargs={"backend_name": f"localtest_{backend_name}_simulator"},
        )
        req = self.client.get(url)
        data = json.loads(req.content)
        self.assertEqual(req.status_code, 200)

        ic(data)
        # get the operational status and see if it is present
        self.assertIn("operational", data)

        # make sure that it has the right status
        self.assertEqual(data["operational"], False)

        # now set the config last queue check to obtain a positive config status
        local_storage.timestamp_queue(backend_name)

        backend_status = local_storage.get_backend_status(backend_name)
        assert backend_status.operational is True

        req = self.client.get(url)
        data = json.loads(req.content)
        self.assertEqual(req.status_code, 200)

        ic(data)
        # get the operational status and see if it is present
        self.assertIn("operational", data)

        # make sure that it has the right status
        self.assertEqual(data["operational"], True)

        # and remove the config
        local_storage._delete_config(backend_name)  # pylint: disable=protected-access
