"""
Agents tools for managing real estate form data in conversations.

This module provides tools to extract field information from user input,
update the conversation state, and check the current status of the form.
"""
import logging

from google.adk.tools.tool_context import ToolContext

from app.utils.state_management import get_form_from_state, update_field_in_form
from app.utils.state_management import is_form_complete, get_missing_fields, get_form_summary

LOG = logging.getLogger(__name__)


def extract_field(field_name: str, value: str, tool_context: ToolContext):
    """
    Extract and store field information in the session state.

    Args:
        field_name: Name of the field to update (will be normalized to snake_case)
        value: Value to store in the field
        tool_context: Context containing the current state

    Returns:
        dict: Status information about the field update operation
    """
    normalized_field_name = field_name.lower().replace(' ', '_')

    LOG.debug('Extracting field: %s with value: %s', normalized_field_name, value)

    standard_fields = ['budget', 'total_size', 'real_estate_type', 'city']
    is_standard_field = normalized_field_name in standard_fields

    # Check if value is already stored to avoid unnecessary updates
    form = get_form_from_state(tool_context.state)
    current_value = None

    if is_standard_field and hasattr(form, normalized_field_name):
        field = getattr(form, normalized_field_name)
        current_value = field.value
    elif not is_standard_field and normalized_field_name in form.additional_fields:
        field = form.additional_fields.get(normalized_field_name)
        current_value = field.value

    if current_value == value:
        LOG.debug('Field %s already has value: %s', normalized_field_name, value)
        return {
            'status': 'unchanged',
            'field': normalized_field_name,
            'value': value,
            'message': 'Field already has this value',
        }

    success, error_msg = update_field_in_form(
        tool_context.state,
        normalized_field_name,
        value,
    )

    if not success:
        LOG.warning('Failed to update field %s: %s', normalized_field_name, error_msg)
        return {
            'status': 'error',
            'field': normalized_field_name,
            'value': value,
            'error': error_msg or 'Validation failed',
        }

    LOG.info('Successfully updated field %s with value: %s', normalized_field_name, value)
    return {
        'status': 'success',
        'field': normalized_field_name,
        'value': value,
        'is_standard_field': is_standard_field,
    }


def check_form_status(tool_context: ToolContext):
    """
    Check the current status of the real estate form.

    Args:
        tool_context: Context containing the current state.

    Returns:
        dict: Form status including completion status, missing fields,
             form summary, and validation attempt count
    """
    LOG.debug('Checking form status')
    missing = get_missing_fields(tool_context.state)
    complete = is_form_complete(tool_context.state)
    summary = get_form_summary(tool_context.state)

    validation_count = tool_context.state.get('form_validation_count', 0)

    if complete:
        LOG.info('Form is complete.')

    return {
        'form_complete': complete,
        'missing_fields': missing,
        'summary': summary,
        'validation_count': validation_count,
    }
