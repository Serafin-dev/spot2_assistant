"""
Form validation agent for real estate property requirements.

This module provides an agent that validates if all required property information 
has been collected and guides the user to provide missing information.
"""
import logging
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from app.agents.tools.tools import check_form_status

LOG = logging.getLogger(__name__)


def before_validator_cb(callback_context: CallbackContext):
    """
    Prepare state before the form validator agent runs.

    Tracks validation attempts to avoid repetitive interactions.

    Args:
        callback_context: Context containing the current state
    """
    # Track validation attempts
    if 'form_validation_count' not in callback_context.state:
        callback_context.state['form_validation_count'] = 0
    else:
        callback_context.state['form_validation_count'] += 1

    LOG.debug('Form validation attempt: %s', callback_context.state["form_validation_count"])


def create_form_validator_agent(model):
    """
    Create an agent specialized in validating form completeness.

    Args:
        model: Language model identifier to use for the agent

    Returns:
        Agent configured for form validation
    """
    LOG.info("Creating form validator agent with model: %s", model)

    instruction = """You are a real estate assistant.
    Your Goal is to validate if all required information has been collected.

    The following fields are required:
    - Budget (e.g., 20,000 USD)
    - Total Size (e.g., 500m²)
    - Real Estate Type (e.g., office, retail, warehouse)
    - City location (e.g., Mexico City)

    Your responsibilities:
    1. Check which fields have been provided and which are missing.
    2. If fields are missing, ask for them in a natural, conversational way.
    3. When all required fields are collected, acknowledge this and provide a summary.
    4. If the user provides new or additional information, update your understanding.

    Always use the `check_form_status` tool to get the current state of the form,
    including which fields are missing.

    IMPORTANT: Be concise and avoid repetition. If you've already asked for specific information,
    don't repeat the same questions in the same message. Ask only for the missing fields that
    you haven't explicitly asked for yet.

    If all required information has been collected, thank the user and:
    1. Summarize all the information you've gathered.
    2. Ask if they would like to provide any additional details or preferences.
    """

    return Agent(
        name='form_validator',
        model=model,
        description='Validates form completeness and guides the user to fill all required fields',
        instruction=instruction,
        tools=[check_form_status],
        before_agent_callback=before_validator_cb,
    )
