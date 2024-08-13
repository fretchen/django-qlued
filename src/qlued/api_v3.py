"""
In this module we define the key feature for the API in v3. This includes the following views:

- get_config: Returns the configuration of the backend.
- get_backend_status: Returns the status of the backend.
- post_job: A view to submit the job to the backend.
- get_job_status: A view to check the job status that was previously submitted to the backend.
- get_job_result: A view to obtain the results of job that was previously submitted to the backend.
- list_backends: Returns the list of backends, excluding any device called "dummy_" 
                as they are test systems.
"""


from decouple import config
from dropbox.exceptions import ApiError, AuthError
from ninja import NinjaAPI
from ninja.security import HttpBearer
from ninja.responses import codes_4xx
from sqooler.schemes import (
    BackendConfigSchemaOut,
    BackendStatusSchemaOut,
    ResultDict,
    StatusMsgDict,
    get_init_status,
)

from django.http import HttpRequest, HttpResponse

from .models import StorageProviderDb, Token
from .schemas import DictSchema
from .storage_providers import (
    get_short_backend_name,
    get_storage_provider,
    get_storage_provider_from_entry,
)


api = NinjaAPI(version="3.0.0")


class InvalidToken(Exception):
    """
    Exception that is raised when the access token is invalid.
    """

@api.exception_handler(InvalidToken)
def on_invalid_token(request: HttpRequest, exc: Exception) -> HttpResponse:
    """
    Exception handler for the InvalidToken exception.
    """
    # pylint: disable=W0613

    job_response_dict = {
        "job_id": "None",
        "status": "None",
        "detail": "None",
        "error_message": "None",
    }
    job_response_dict["status"] = "ERROR"
    job_response_dict["error_message"] = "Invalid credentials!"
    job_response_dict["detail"] = "Invalid credentials!"

    return api.create_response(request, job_response_dict, status=401)


class AuthBearer(HttpBearer):
    """
    Class that handles authentification through a token.
    """
    # pylint: disable=R0903
    def authenticate(self, request: HttpRequest, token: str) -> str:

        try:
            Token.objects.get(key=token)
            return token
        except Token.DoesNotExist as f:
            raise InvalidToken from f


@api.get(
    "{backend_name}/get_config",
    response={200: BackendConfigSchemaOut, codes_4xx: StatusMsgDict},
    tags=["Backend"],
    url_name="get_config",
)
def get_config(request, backend_name: str):
    """
    Returns the configuration of the backend. This is an API implementation of the class
    `qiskit.providers.models.BackendConfiguration`

    Args:
        request: The request object.
        backend_name: The name of the backend.

    Returns:
        The configuration of the backend.

    Raises:
        404: If the backend is not found.
    """
    # pylint: disable=W0613

    # we have to split the name into several parts by `_`. If there is only one part, then we
    # assume that the user has given the short name of the backend. If there are more parts, then
    # we assume that the user has given the full name of the backend.
    short_backend = get_short_backend_name(backend_name)
    if not short_backend:
        job_response_dict = {
            "job_id": "None",
            "status": "ERROR",
            "detail": (
                f"Unknown back-end {backend_name}! The string should have 1 or "
                f"three parts separated by `_`!"
            ),
            "error_message": "Unknown back-end!",
        }
        return 404, job_response_dict

    try:
        storage_provider = get_storage_provider(backend_name)
    except StorageProviderDb.DoesNotExist:
        job_response_dict = {
            "job_id": "None",
            "status": "ERROR",
            "detail": (
                f"Unknown back-end {backend_name}! The string should have 1 or"
                f" three parts separated by `_`!"
            ),
            "error_message": "Unknown back-end!",
        }
        return 404, job_response_dict

    config_info = storage_provider.get_backend_dict(short_backend)
    # we have to add the URL to the backend configuration
    base_url = config("BASE_URL")

    if config_info.simulator:
        full_backend_name = f"{storage_provider.name}_{short_backend}_simulator"
    else:
        full_backend_name = f"{storage_provider.name}_{short_backend}_hardware"

    config_info.url = base_url + "/api/v2/" + full_backend_name + "/"

    return config_info


@api.get(
    "{backend_name}/get_backend_status",
    response={200: BackendStatusSchemaOut, codes_4xx: StatusMsgDict},
    tags=["Backend"],
    url_name="get_backend_status",
)
def get_backend_status(request, backend_name: str):
    """
    Returns the status of the backend. This is an API implementation of the class
    `qiskit.providers.models.BackendStatus`

    Args:
        request: The request object.
        backend_name: The name of the backend.

    Returns:
        The status of the backend.

    Raises:
        404: If the backend is not found.
    """
    # pylint: disable=W0613

    # we have to split the name into several parts by `_`. If there is only one part, then we
    # assume that the user has given the short name of the backend. If there are more parts, then
    # we assume that the user has given the full name of the backend.
    short_backend = get_short_backend_name(backend_name)
    if not short_backend:
        job_response_dict = {
            "job_id": "None",
            "status": "ERROR",
            "detail": "Unknown back-end! The string should have 1 or three parts separated by `_`!",
            "error_message": "Unknown back-end!",
        }
        return 404, job_response_dict

    try:
        storage_provider = get_storage_provider(backend_name)
    except FileNotFoundError:
        job_response_dict = {
            "job_id": "None",
            "status": "ERROR",
            "detail": "Unknown back-end! The string should have 1 or three parts separated by `_`!",
            "error_message": "Unknown back-end!",
        }
        return 404, job_response_dict
    return storage_provider.get_backend_status(short_backend)


@api.post(
    "{backend_name}/post_job",
    response={200: StatusMsgDict, codes_4xx: StatusMsgDict},
    tags=["Backend"],
    url_name="post_job",
    auth=AuthBearer(),
)
def post_job(request, data: DictSchema, backend_name: str):
    """
    A view to submit the job to the backend.
    """
    # the token is stored in the request object as the attribute auth
    # the user has to provider it during identification
    api_key = request.auth

    # pylint: disable=R0914, W0613
    job_response_dict = {
        "job_id": "None",
        "status": "None",
        "detail": "None",
        "error_message": "None",
    }

    token = Token.objects.get(key=api_key)

    username = token.user.username
    # get the proper backend name
    short_backend = get_short_backend_name(backend_name)
    # now it is time to look for the backend
    storage_provider = get_storage_provider(backend_name)
    backend_names = storage_provider.get_backends()
    if short_backend not in backend_names:
        job_response_dict["status"] = "ERROR"
        job_response_dict["detail"] = "Unknown back-end!"
        job_response_dict["error_message"] = "Unknown back-end!"
        return 404, job_response_dict

    # as the backend is known, we can now try to submit the job
    job_dict = data.payload
    try:
        storage_provider = get_storage_provider(backend_name)

        # upload the job to the backend via the storage provider
        job_id = storage_provider.upload_job(
            job_dict=job_dict, display_name=short_backend, username=username
        )

        # now we upload the status json to the backend. this is the same status json
        # that is returned to the user
        job_response_dict = storage_provider.upload_status(
            display_name=short_backend,
            username=username,
            job_id=job_id,
        )
        return job_response_dict
    except (AuthError, ApiError):
        job_response_dict["status"] = "ERROR"
        job_response_dict["detail"] = "Error saving json data to database!"
        job_response_dict["error_message"] = "Error saving json data to database!"
        return 406, job_response_dict


@api.get(
    "{backend_name}/get_job_status",
    response={200: StatusMsgDict, codes_4xx: StatusMsgDict},
    tags=["Backend"],
    url_name="get_job_status",
    auth=AuthBearer(),
)
def get_job_status(request, backend_name: str, job_id: str):
    """
    A view to check the job status that was previously submitted to the backend.
    """
    # pylint: disable=W0613
    job_response_dict = get_init_status()
    token = request.auth
    token_object = Token.objects.get(key=token)
    username = token_object.user.username
    storage_provider = get_storage_provider(backend_name)
    backend_names = storage_provider.get_backends()
    short_backend = get_short_backend_name(backend_name)
    if short_backend not in backend_names:
        job_response_dict.status = "ERROR"
        job_response_dict.detail = "Unknown back-end!"
        job_response_dict.error_message = "Unknown back-end!"
        return 404, job_response_dict

    job_response_dict.job_id = job_id

    storage_provider = get_storage_provider(backend_name)

    job_response_dict = storage_provider.get_status(
        display_name=short_backend, username=username, job_id=job_id
    )
    if job_response_dict.status == "ERROR":
        return 406, job_response_dict
    return 200, job_response_dict


@api.get(
    "{backend_name}/get_job_result",
    response={200: StatusMsgDict | ResultDict, codes_4xx: StatusMsgDict},
    tags=["Backend"],
    url_name="get_job_result",
    auth=AuthBearer(),
)
def get_job_result(request, backend_name: str, job_id: str):
    """
    A view to obtain the results of job that was previously submitted to the backend.
    """
    # pylint: disable=W0613
    status_msg_draft = {
        "job_id": "None",
        "status": "None",
        "detail": "None",
        "error_message": "None",
    }

    token = request.auth
    token_object = Token.objects.get(key=token)

    username = token_object.user.username
    short_backend = get_short_backend_name(backend_name)
    storage_provider = get_storage_provider(backend_name)
    backend_names = storage_provider.get_backends()
    if short_backend not in backend_names:
        status_msg_draft["status"] = "ERROR"
        status_msg_draft["detail"] = "Unknown back-end!"
        status_msg_draft["error_message"] = "Unknown back-end!"
        return 404, status_msg_draft

    # request the data from the queue
    status_msg_dict = storage_provider.get_status(
        display_name=short_backend, username=username, job_id=job_id
    )
    if status_msg_dict.status == "ERROR":
        return 406, status_msg_dict
    if status_msg_dict.status != "DONE":
        return 200, status_msg_dict
    # and if the status is switched to done, we can also obtain the result
    result_dict = storage_provider.get_result(
        display_name=short_backend, username=username, job_id=job_id
    )

    return 200, result_dict


@api.get(
    "/backends",
    response=list[BackendConfigSchemaOut],
    tags=["Backend"],
    url_name="get_backends",
)
def list_backends(request):
    """
    Returns the list of backends, excluding any device called "dummy_" as they are test systems.
    """
    # pylint: disable=W0613, E1101

    backend_list = []

    # obtain all the available storage providers from the database
    storage_provider_entries = StorageProviderDb.objects.all()

    # now loop through them and obtain the backends
    for storage_provider_entry in storage_provider_entries:
        if not storage_provider_entry.is_active:
            continue
        storage_provider = get_storage_provider_from_entry(storage_provider_entry)

        backend_names = storage_provider.get_backends()
        for backend in backend_names:
            # for testing we created dummy devices. We should ignore them in any other cases.
            if not "dummy" in backend:
                config_dict = storage_provider.get_backend_dict(backend)
                backend_list.append(config_dict)
    return backend_list
