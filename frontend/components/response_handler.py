"""
Response handling component.

Processes user messages and handles streaming responses from the assistant.
"""
import asyncio
import logging
import time

import streamlit as st

from frontend.services.assistant_service import get_streaming_response

LOG = logging.getLogger(__name__)


def handle_response():
    """
    Processes pending messages and displays streaming responses.

    Checks for queued messages, sends them to the assistant,
    and handles the streaming response display with smooth transitions.
    """
    # Use session state to maintain response element between reruns
    if 'response_placeholder_key' not in st.session_state:
        st.session_state.response_placeholder_key = 'response_element'

    response_container = st.container()

    with response_container:
        response_element = st.empty()

    if st.session_state.message_to_process:
        user_message = st.session_state.message_to_process
        st.session_state.message_to_process = None

        LOG.info('Processing user message: %s...', user_message[:30])

        def get_response():
            """
            Retrieves and processes streaming response from the assistant.

            Manages the asyncio event loop, accumulates streaming text chunks,
            handles error cases, and updates the chat history when complete.
            """
            final_text_response = ''  # Variable to store final result
            loop = asyncio.new_event_loop()

            try:
                async def process_stream():
                    local_response_acc = ''          # To accumulate text from partial chunks
                    final_complete_text = None       # To store text from final (non-partial) chunk

                    LOG.debug('Starting streaming response')
                    async for chunk in get_streaming_response(user_message):
                        is_partial_chunk = chunk.get('partial', False)

                        # If partial and has text, accumulate
                        if chunk['text'] and is_partial_chunk:
                            local_response_acc += chunk['text']
                            response_element.markdown(f"**Assistant:** {local_response_acc}")

                        # If NOT partial and has text, it's the complete final text
                        elif chunk['text'] and not is_partial_chunk:
                            final_complete_text = chunk['text']
                            response_element.markdown(f"**Assistant:** {final_complete_text}")

                        if chunk.get('done', False):
                            LOG.debug('Streaming response completed')
                            break

                    return final_complete_text if final_complete_text is not None else local_response_acc

                # Execute async processing and CAPTURE the returned value
                final_text_response = loop.run_until_complete(process_stream())
                LOG.info('Response generated successfully')

            except (asyncio.TimeoutError, ConnectionError, ValueError) as e:
                LOG.error('Error in get_response: %s', e)
                final_text_response = f'Sorry, I encountered an error: {str(e)}'
                response_element.markdown(f"**Assistant:** {final_text_response}")
                st.error(f'Error processing stream: {e}')  # Show error in UI
            finally:
                loop.close()

            # Add the complete response to history
            if isinstance(final_text_response, str) and final_text_response:
                st.session_state.chat_history.append({'role': 'assistant', 'content': final_text_response})

                # IMPORTANT: Keep the final response visible in the placeholder
                # until the rerun completes to avoid a "flash" effect
                time.sleep(0.2)  # Short delay to ensure UI is updated

                st.rerun()
            else:
                LOG.warning('Skipping history append: Invalid response type: %s', type(final_text_response))
                st.rerun()
        get_response()
    else:
        # If we just completed a response and reran the app,
        # clear the response element now that the history is updated
        if st.session_state.chat_history and len(st.session_state.chat_history) > 0:
            response_element.empty()
