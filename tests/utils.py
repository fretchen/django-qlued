"""
Some helper functions for the tests.
"""
from typing import Tuple
import uuid
from sqooler.schemes import BackendConfigSchemaIn

def get_dummy_config(sign: bool = True) -> Tuple[str, BackendConfigSchemaIn]:
    """
    Generate the dummy config of the fermion type.

    Args:
        sign: Whether to sign the files.
    Returns:
        The backend name and the backend config input.
    """

    dummy_id = uuid.uuid4().hex[:5]
    backend_name = f"dummy{dummy_id}"

    dummy_dict: dict = {}
    dummy_dict["gates"] = []
    dummy_dict["display_name"] = backend_name
    dummy_dict["num_wires"] = 3
    dummy_dict["version"] = "0.0.1"
    dummy_dict["description"] = "This is a dummy backend."
    dummy_dict["cold_atom_type"] = "fermion"
    dummy_dict["max_experiments"] = 1
    dummy_dict["max_shots"] = 1
    dummy_dict["simulator"] = True
    dummy_dict["supported_instructions"] = []
    dummy_dict["wire_order"] = "interleaved"
    dummy_dict["num_species"] = 1
    dummy_dict["operational"] = True
    dummy_dict["sign"] = sign

    backend_info = BackendConfigSchemaIn(**dummy_dict)
    return backend_name, backend_info
