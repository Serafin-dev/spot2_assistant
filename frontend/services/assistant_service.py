"""
Assistant service.

Provides functionality to interact with the backend assistant.
"""
import logging
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st

from app.main import assistant

LOG = logging.getLogger(__name__)


async def get_streaming_response(message):
    """
    Gets a streaming response from the assistant.

    Args:
        message: The user message to process

    Yields:
        Chunks of the assistant's response
    """
    try:
        async for chunk in assistant.run_streaming(
            user_id=st.session_state.user_id,
            session_id=st.session_state.session_id,
            message=message,
        ):
            yield chunk
    except (ConnectionError, ValueError, RuntimeError) as e:
        LOG.error('Error in streaming response: %s', str(e))
        yield {'text': f'Error: {str(e)}', 'done': True, 'partial': False}
