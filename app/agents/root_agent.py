"""
Root coordinator agent for the real estate assistant.

This module provides the main orchestrating agent that manages conversation flow
and delegates to specialized agents for field extraction and validation.
"""
import logging
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from ..models.property_form import PropertyFormModel

LOG = logging.getLogger(__name__)


def before_root_cb(callback_context: CallbackContext):
    """
    Callback executed before the root agent to prevent repetitions.

    Args:
        callback_context: Context containing the current state
    """
    if 'conversation_turn' not in callback_context.state:
        callback_context.state['conversation_turn'] = 1
        LOG.debug('Starting new conversation')
    else:
        callback_context.state['conversation_turn'] += 1
        LOG.debug('Conversation turn: %s', callback_context.state["conversation_turn"])


def create_root_agent(model):
    """
    Create the main coordinator agent.

    Args:
        model: Language model identifier to use for the agent

    Returns:
        Agent configured as the main conversation coordinator
    """
    LOG.info('Creating root coordinator agent with model: %s', model)

    # Get form fields for instruction generation
    form = PropertyFormModel()
    fields_map = {
        'Budget': form.budget,
        'Total Size': form.total_size,
        'Real Estate Type': form.real_estate_type,
        'City': form.city
    }

    field_descriptions = [f'- {name}: {field.description}' for name, field in fields_map.items()]
    fields_text = '\n'.join(field_descriptions)

    instruction = f"""You work as an orchestrator of real estate assistants helping users find commercial properties.

    Your primary goal is to collect the following required information from the user:
    {fields_text}

    Additionally, you should collect any other relevant property preferences the user might have.

    Guidelines:
    1. Be conversational and friendly while guiding the user.
    2. ONLY when the conversation needs it, acknowledge the information you've already collected. You can provide that
       information to the user if asked. Also you can show it at the beginning of the conversation to let the user know
       what information you need, and when you have finished collecting all the required information.
    3. Ask for missing information to the user only if the conversation flow enables it.
    4. If the user provides new or updated information, update your records.
    5. IMPORTANT: Be concise and avoid repetition. Do not repeat the same questions in a single response.

    Ask for additional information until the user lets you know they are done.

    If you notice a user is confused by repetitive questions, apologize and try to keep the conversation on track
    by focusing only on one missing piece of information at a time.
    """

    return Agent(
        name='real_estate_coordinator',
        model=model,
        description='Coordinates the real estate property inquiry conversation',
        instruction=instruction,
        before_agent_callback=before_root_cb,
    )
