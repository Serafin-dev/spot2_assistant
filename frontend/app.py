"""
Streamlit frontend for the Real Estate Assistant application - Main entry point.

This module serves as the entry point for the Streamlit application,
initializing the app and orchestrating the different components.
"""
import os
import sys
import logging

# Configure sys.path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import streamlit as st
from frontend.utils.session_manager import initialize_session
from frontend.components.chat_display import render_chat_history
from frontend.components.message_input import render_message_input
from frontend.components.response_handler import handle_response

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
LOG = logging.getLogger(__name__)

st.set_page_config(
    page_title='spot2 Assistant',
    page_icon='🏢',
    layout='wide',
)

LOG.info('Starting Streamlit frontend for spot2 Assistant')

initialize_session()

st.title('🏢 spot2 Assistant')
st.markdown("I'll help you find the perfect commercial property. Tell me about your requirements!")

# Create layout with specific ordering
main_container = st.container()
with main_container:
    chat_section = st.container()
    with chat_section:
        render_chat_history()

    response_section = st.container()
    with response_section:
        handle_response()

    input_section = st.container()
    with input_section:
        render_message_input()

st.markdown('---')
st.markdown("""
**Required Information:**
- Budget (e.g., "I have a budget of 20,000 USD")
- Total Size (e.g., "I need 500m²")
- Real Estate Type (e.g., "I am looking for an office")
- City (e.g., "I want a property in Mexico City")

Feel free to provide any additional preferences!
""")
