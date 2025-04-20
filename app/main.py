'''
Real estate chatbot assistant orchestrating specialized agents.

Manages sessions, agent coordination (extraction, validation), and conversation modes.
'''

import uuid
import logging
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.genai.types import Content, Part
from google.adk.tools.agent_tool import AgentTool

from app.settings import MODEL_ID, APP_NAME, DEBUG_MODE
from app.agents.root_agent import create_root_agent
from app.agents.field_extractor import create_field_extractor_agent
from app.agents.form_validator import create_form_validator_agent
from app.utils.state_management import initialize_form_in_state

logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
LOG = logging.getLogger(__name__)


class Spot2Assistant:
    '''
    Orchestrates specialized agents for a real estate chatbot.

    Manages user sessions, coordinates field extraction/validation agents,
    and handles sync/streaming conversations.
    '''
    def __init__(self):
        '''Initialize the assistant.'''
        self.session_service = InMemorySessionService()
        self.root_agent = create_root_agent(MODEL_ID)
        self.field_extractor = create_field_extractor_agent(MODEL_ID)
        self.form_validator = create_form_validator_agent(MODEL_ID)

        self.root_agent.tools = [
            AgentTool(agent=self.field_extractor),
            AgentTool(agent=self.form_validator),
        ]

        self.runner = Runner(
            app_name=APP_NAME,
            agent=self.root_agent,
            session_service=self.session_service
        )
        self.active_requests = {}

    def _get_or_create_session(self, user_id, session_id):
        '''Get existing session or create a new one if it doesn't exist.'''
        try:
            return self.session_service.get_session(
                app_name=APP_NAME,
                user_id=user_id,
                session_id=session_id
            )
        except ValueError:
            session = self.create_session(user_id, session_id)
            LOG.info('Created new session: %s', session_id)
            return session

    def _setup_live_request(self, session_id):
        '''Set up and register a new live request queue.'''
        live_request_queue = LiveRequestQueue()

        self.active_requests[session_id] = {
            'request_queue': live_request_queue
        }

        return live_request_queue

    async def _cancel_previous_requests(self, session_id):
        '''Cancel any active request for the given session.'''
        if session_id in self.active_requests:
            LOG.debug('Canceling previous request for session %s', session_id)
            try:
                previous_queue = self.active_requests[session_id].get('request_queue')
                if previous_queue:
                    previous_queue.close()
            except (AttributeError, RuntimeError) as e:
                LOG.error('Error closing previous request: %s', e)

            self.active_requests[session_id] = {}

    async def _process_live_events(self, live_events, session_id):
        '''Process streaming events and generate response chunks.'''
        async for event in live_events:
            text_content = ''
            is_partial = event.partial or False
            is_done = event.turn_complete or False

            if event.content and event.content.parts and event.content.parts[0].text:
                text_content = event.content.parts[0].text
                text_length = len(text_content)

                if is_done:
                    LOG.debug('Completed response stream for session %s, final length: %s',
                              session_id, text_length)

            yield {
                'text': text_content,
                'done': is_done,
                'partial': is_partial
            }

    async def _cleanup_resources(self, session_id, live_request_queue):
        '''Clean up resources after streaming completes or fails.'''
        try:
            LOG.debug('Finishing stream handling for session %s', session_id)
            if session_id in self.active_requests:
                try:
                    live_request_queue.close()
                except (AttributeError, RuntimeError) as e:
                    LOG.error('Error closing request queue: %s', e)

                self.active_requests[session_id] = {}
        except (KeyError, TypeError) as e:
            LOG.error('Error during cleanup: %s', e)

    def create_session(self, user_id=None, session_id=None):
        '''
        Create a new conversation session with initialized form state.

        Args:
            user_id: Optional user identifier
            session_id: Optional session identifier

        Returns:
            Session object ready for conversation
        '''
        if user_id is None:
            user_id = f'user_{uuid.uuid4().hex[:8]}'
        if session_id is None:
            session_id = f'session_{uuid.uuid4().hex[:8]}'

        LOG.info('Creating new session: user_id=%s, session_id=%s', user_id, session_id)

        session = self.session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id
        )

        initialize_form_in_state(session.state)

        return session

    def run(self, user_id, session_id, message):
        '''
        Process a user message in synchronous mode.

        Args:
            user_id: User identifier
            session_id: Session identifier
            message: Text message from user

        Returns:
            Final text response from assistant
        '''
        content = Content(role='user', parts=[Part(text=message)])
        events = self.runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        )

        final_response = None
        for event in events:
            if event.is_final_response() and event.content and event.content.parts:
                final_response = event.content.parts[0].text

        return final_response

    async def run_streaming(self, user_id, session_id, message):
        '''
        Process a user message in streaming mode, yielding partial responses.

        Args:
            user_id: User identifier
            session_id: Session identifier
            message: Text message from user

        Yields:
            Dict containing text response parts, completion status, and partial flags
        '''
        # 1. Prepare session and resources
        await self._cancel_previous_requests(session_id)
        session = self._get_or_create_session(user_id, session_id)
        content = Content(role='user', parts=[Part(text=message)])

        # 2. Configure live request
        live_request_queue = self._setup_live_request(session_id)
        run_config = RunConfig(response_modalities=['TEXT'])

        try:
            LOG.info('Starting live request for session %s with message length: %s',
                     session_id, len(message))
            live_events = self.runner.run_live(
                session=session,
                live_request_queue=live_request_queue,
                run_config=run_config
            )

            live_request_queue.send_content(content=content)
            LOG.debug('Sent user message for session %s', session_id)

            async for response in self._process_live_events(live_events, session_id):
                yield response

            LOG.debug('Finished processing events for session %s', session_id)

        except (ValueError, RuntimeError, AttributeError) as e:
            LOG.error('Error in streaming response: %s', str(e), exc_info=True)
            yield {'text': f'Error: {str(e)}', 'done': True, 'partial': False}
        finally:
            await self._cleanup_resources(session_id, live_request_queue)

assistant = Spot2Assistant()
