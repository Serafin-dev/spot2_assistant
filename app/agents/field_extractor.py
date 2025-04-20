"""
Field extraction agent for real estate property requirements.

This module provides an agent that extracts property information fields
from user messages and updates the conversation state accordingly.
"""
import logging
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from app.utils.state_management import get_form_from_state, update_form_in_state
from app.utils.state_management import PropertyFormModel
from app.agents.tools.tools import extract_field

LOG = logging.getLogger(__name__)


def before_agent_cb(callback_context: CallbackContext):
    """
    Prepare state before the field extractor agent runs.

    Ensures property form exists in state and tracks extraction attempts.

    Args:
        callback_context: Context containing the current state
    """
    if "property_form" not in callback_context.state:
        LOG.debug('Initializing property form in state')
        form = get_form_from_state(callback_context.state)
        update_form_in_state(callback_context.state, form)

    # Track extraction attempts
    if 'extraction_count' not in callback_context.state:
        callback_context.state['extraction_count'] = 1
    else:
        callback_context.state['extraction_count'] += 1

    LOG.debug('Field extraction attempt: %s', callback_context.state["extraction_count"])


def create_field_extractor_agent(model):
    """
    Create an agent specialized in extracting fields from user messages.

    Args:
        model: Language model identifier to use for the agent

    Returns:
        Agent configured for field extraction
    """
    LOG.info('Creating field extractor agent with model: %s', model)

    form = PropertyFormModel()

    field_descriptions = []
    fields_map = {
        'budget': form.budget,
        'total_size': form.total_size,
        'real_estate_type': form.real_estate_type,
        'city': form.city,
    }

    for name, field in fields_map.items():
        examples = ", ".join([f'"{ex}"' for ex in field.examples])
        field_descriptions.append(f'- {name}: {field.description} (Examples: {examples}).')

    fields_text = "\n".join(field_descriptions)

    instruction = f"""You are a specialized agent for extracting real estate property requirements from user messages.

    Your task is to identify and extract these specific fields from the user's messages:
    {fields_text}

    You should also extract any additional property preferences the user mentions, like:
    - Location preferences (downtown, suburban)
    - Amenities (parking, security)
    - Time frame (when they need the property)
    - Any other relevant property details

    For each field you identify in the user's message:
    1. Determine the field name
    2. Extract the exact value provided by the user
    3. Decide if it belongs to one of the required fields or should be an additional field
    4. Use the `extract_field` tool to save the field to the session state

    Be thorough and extract ALL fields mentioned in EACH message, not just one field at a time.
    Do not extract the same field multiple times if it hasn't changed.
    """

    return Agent(
        name='field_extractor',
        model=model,
        description='Extracts and validates fields from user messages',
        instruction=instruction,
        tools=[extract_field],
        before_agent_callback=before_agent_cb,
    )
