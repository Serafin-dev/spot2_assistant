"""
Utilities for property form state management.

This module contains functions to manipulate the property form state
in the ADK session. It provides methods to initialize, retrieve,
update, and validate form data.
"""
from typing import Dict, Any, Optional
from app.models.property_form import PropertyFormModel


def initialize_form_in_state(state: Dict[str, Any]) -> None:
    """
    Initialize the form in the session state if it doesn't exist.

    Checks if a property form exists in the current session state.
    If not, creates a new model instance and stores it in the state.

    Args:
        state: ADK session state dictionary
    """
    if 'property_form' not in state:
        state['property_form'] = PropertyFormModel().model_dump()

def get_form_from_state(state: Dict[str, Any]) -> PropertyFormModel:
    """
    Retrieve the form model from the session state.

    Ensures the form is initialized in the state before retrieving it.
    Converts the state data into a validated model instance.

    Args:
        state: ADK session state dictionary

    Returns:
        PropertyFormModel instance with current data
    """
    initialize_form_in_state(state)
    return PropertyFormModel.model_validate(state['property_form'])

def update_form_in_state(state: Dict[str, Any], form: PropertyFormModel) -> None:
    """
    Update the session state with form data.
    Converts the model instance to a dictionary and stores it in the state.

    Args:
        state: ADK session state dictionary
        form: PropertyFormModel instance with updated data
    """
    state['property_form'] = form.model_dump()

def update_field_in_form(state: Dict[str, Any], field_name: str, value: str) -> tuple[bool, Optional[str]]:
    """
    Update a specific field in the form.

    Gets the current form, updates the specified field with the new value,
    and saves the changes to the state. Returns the result of the operation.

    Args:
        state: ADK session state dictionary
        field_name: Name of the field to update
        value: New value for the field

    Returns:
        Tuple of (success, error_message):
            - success: True if the update was successful, False otherwise
            - error_message: Description of the error if one occurred, None if successful
    """
    form = get_form_from_state(state)
    success, error_msg = form.update_field(field_name, value)
    update_form_in_state(state, form)
    return success, error_msg

def is_form_complete(state: Dict[str, Any]) -> bool:
    """
    Check if the form is complete.

    A form is considered complete when all required fields
    have valid values.

    Args:
        state: ADK session state dictionary

    Returns:
        True if all required fields are complete, False otherwise
    """
    form = get_form_from_state(state)
    return form.is_complete()

def get_missing_fields(state: Dict[str, Any]) -> list[str]:
    """
    Get the list of missing required fields.

    Identifies and returns the names of required fields that don't yet have
    valid values in the form.

    Args:
        state: ADK session state dictionary

    Returns:
        List of missing required field names
    """
    form = get_form_from_state(state)
    return form.get_missing_fields()

def get_form_summary(state: Dict[str, Any]) -> str:
    """
    Get a readable summary of the form state.

    Generates a Markdown-formatted representation of the current form state,
    including the values of each field and its validation status.

    Args:
        state: ADK session state dictionary

    Returns:
        Markdown-formatted string describing the form state
    """
    form = get_form_from_state(state)
    return form.get_fields_summary()
