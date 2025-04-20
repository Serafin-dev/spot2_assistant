# 🏢 Real Estate Assistant

An conversational application that uses LLMs to collect and manage commercial real estate requirements.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

## 📋 Description

Spot2 Assistant is an application based on Google's Agent Development Kit (ADK) that facilitates capturing commercial real estate requirements through a conversational interface. The system uses a multi-agent architecture to extract information, validate forms, and maintain a natural conversation with the user.

The application automatically identifies and extracts key information about the user's real estate needs (such as budget, size, property type, and location) while maintaining a fluid and natural conversation.

## ✨ Key Features

- 💬 Conversational chat interface with real-time responses (streaming)
- 🔍 Automatic field extraction from user text
- ✅ Intelligent validation of collected information
- 📊 Visualization of the current form state
- 🧠 Specialized multi-agent architecture
- 🔄 Support for updating previously provided information
- 📝 Capture of additional preferences

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- Google AI API key to access Gemini models

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/real-estate-chatbot.git
cd spot2-assistant
```

2. Create and activate a virtual environment:
```bash
virtualenv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
make requirements
```

4. Configure the API Key:
```bash
cp .env.example .env
```

5. Edit the `.env` file adding your Google AI API key:
```
GOOGLE_API_KEY=your-api-key-here
```

### Local Execution

To run the application in development mode:
```bash
make run
```

The application will be available at http://localhost:8501

### Using Docker

You can also run the application using Docker:

```bash
make build
make run-container
```

## 🏗️ Architecture

The application follows an architecture based on specialized agents:

### Main Components

1. **Root Agent (Coordinator)**:
   - Handles the main interaction and coordinates specialized agents
   - Maintains natural conversational flow
   - Determines which agent should be invoked at each moment

2. **Field Extractor Agent**:
   - Specialized in extracting specific information from user text
   - Identifies fields such as budget, size, property type, and location
   - Updates the conversation state with the extracted information

3. **Form Validator Agent**:
   - Verifies form completeness
   - Identifies missing fields
   - Guides the user to obtain pending information

### State Management

The conversation state is managed using:

- Pydantic models for validation and data structure
- ADK state system for persistence between conversation turns
- Conversion between state representations and objects to facilitate operations

## 🔧 Technologies Used

- **Google ADK**: Framework for conversational agent development
- **Streamlit**: Web user interface framework
- **Pydantic**: Data validation and serialization
- **Python-dotenv**: Environment variable management
- **Docker**: Containerization for deployment

## 🌐 Deployment

For production deployment, it is recommended:

### Google Cloud Run

```bash
# Build the image
docker build -t gcr.io/your-project/spot2-assistant .

# Push to Container Registry
docker push gcr.io/your-project/spot2-assistant

# Deploy to Cloud Run
gcloud run deploy spot2-assistant \
  --image gcr.io/your-project/spot2-assistant \
  --platform managed \
  --set-env-vars GOOGLE_API_KEY=your_key_here
```

## 🧑‍💻 Development

### Project Structure

```
real-estate-chatbot/
├── app/                      # Backend main logic
│   ├── agents/               # Specialized agents implementation
│   ├── models/               # Data models (Pydantic)
│   └── utils/                # Utilities and state management
├── frontend/                 # Streamlit user interface
│   ├── components/           # Reusable UI components
│   └── services/             # Services for backend communication
├── requirements/             # Dependency files
└── tests/                    # Automated tests
```

### Run Tests

```bash
make test
```

### Check Code Quality

```bash
# Run linters and formatters
make quality
```

## Scalability and Limitations

### Current Limitations

The current implementation uses `InMemorySessionService` to manage user sessions, which presents the following limitations:

- **Limited persistence**: All sessions are stored in memory and are lost when the application restarts.
- **Limited horizontal scalability**: It is not possible to share sessions between multiple instances of the application.
- **Limited memory capacity**: The number of simultaneous sessions is limited by the available memory on a single machine.

### Improvements for Scalability

To convert this application into a scalable solution for production use with many simultaneous users, the following improvements are recommended:

#### 1. Session Persistence

**Recommended options:**

- **DatabaseSessionService**: ADK provides an implementation that uses relational databases (PostgreSQL, MySQL, SQLite) to store sessions.
  ```python
  from google.adk.sessions import DatabaseSessionService
  session_service = DatabaseSessionService(db_url="postgresql://user:pass@host/dbname")
  ```

- **Cloud services**: For applications deployed on Google Cloud, `VertexAiSessionService` can be used.

For more information about persistence options, see the [official ADK documentation on sessions](https://google.github.io/adk-docs/sessions/session/#sessionservice-implementations).

#### 2. Distributed Architecture

- **Load balancing**: Implement a load balancer in front of multiple application instances.
- **Frontend/backend separation**: Consider separating the user interface (Streamlit) from the business logic (API).

#### 3. Monitoring and Performance

- **Metrics**: Add performance and usage metrics. Currently, there is no clear notion of consumption.

#### 4. Resource Optimization

- **Resource adjustment**: Define appropriate CPU and memory limits for containers.
- **Session timeout**: Configure an appropriate expiration time for inactive sessions.

### Recommendation

For a scalable production implementation, it is recommended:

1. Migrate to `DatabaseSessionService` with a robust database such as PostgreSQL or Redis.
2. Deploy the application in containers (Docker) to facilitate scalability.
An API could be created in /app/api with websocket integration to communicate with other services. This would allow integration with other apps/services and distribute services separately, e.g., one container for backend, another for frontend. This also allows the use of multiple instances.
3. Use a container orchestrator (Kubernetes) to manage multiple instances.
4. Implement a load balancer.

### Additional Resources

- [ADK Sessions Documentation](https://google.github.io/adk-docs/sessions/)
- [Google ADK Implementation Guide](https://google.github.io/adk-docs/implementation/overview/)
- [Best Practices for Scalable Applications](https://cloud.google.com/architecture/scalable-and-resilient-apps)

```mermaid
flowchart TD
    %% Styles
    classDef frontend fill:#d4f1f9,stroke:#05728f,stroke-width:1px
    classDef backend fill:#e1d5e7,stroke:#9673a6,stroke-width:1px
    classDef agent fill:#fff2cc,stroke:#d6b656,stroke-width:1px
    classDef state fill:#d5e8d4,stroke:#82b366,stroke-width:1px
    classDef decision fill:#f8cecc,stroke:#b85450,stroke-width:1px

    %% Main nodes
    Start([User starts application]) --> Init[Initialize session\nstreamlit]
    Init --> InitForm[Initialize empty\nPropertyFormModel]
    InitForm --> UI[Display chat\ninterface]
    UI --> UserInput[User writes message]

    %% Message flow
    UserInput --> CaptureMessage[Capture message\nmessage_input.py]
    CaptureMessage --> StoreMessage[Save in chat_history]
    StoreMessage --> QueueMessage[Mark message for processing\nmessage_to_process]
    QueueMessage --> ResponseHandler[Start response_handler.py]

    %% Backend processing
    ResponseHandler --> StreamingInit[Initialize streaming\nassistant.run_streaming]
    StreamingInit --> LiveQueue[Create LiveRequestQueue]
    LiveQueue --> RootAgent[Root Agent\nCoordinator]

    %% Specialized agents
    RootAgent --> ExtractorAgent[Field Extractor Agent]
    ExtractorAgent --> ExtractFields[Extract fields\nbudget, size, type, city]
    ExtractFields --> UpdateForm[Update PropertyFormModel]

    %% Field validation
    UpdateForm --> ValidatorAgent[Form Validator Agent]
    ValidatorAgent --> CheckStatus[Check form status]

    %% Decision based on completeness
    CheckStatus --> IsComplete{Is form complete?}
    IsComplete -->|No| GenerateMissing[Generate response\nfor missing fields]
    IsComplete -->|Yes| GenerateSummary[Generate summary\nof collected information]

    %% Response streaming
    GenerateMissing --> ResponseStream[Send response\nvia streaming]
    GenerateSummary --> ResponseStream
    ResponseStream --> RenderResponse[Render response\nin frontend]

    %% UI update
    RenderResponse --> UpdateHistory[Update chat\nhistory]
    UpdateHistory --> Ready[Ready for next\nmessage]
    Ready --> UserInput

    %% Submodules and details
    subgraph FormState[Form state]
        Validate[Validate field\nformat] --> StatusUpdate[Update status\nVALID/INVALID]
        StatusUpdate --> AdditionalFields[Store additional\nfields]
        AdditionalFields --> CheckComplete[Check form\ncompleteness]
    end

    UpdateForm --> Validate

    subgraph FieldProcessing[Field processing]
        Budget[Extract Budget]
        Size[Extract Size]
        PropType[Extract Property Type]
        City[Extract City]
        ExtraFields[Extract Additional Fields]
    end

    ExtractFields --> Budget
    ExtractFields --> Size
    ExtractFields --> PropType
    ExtractFields --> City
    ExtractFields --> ExtraFields

    %% Apply styles
    class Init,CaptureMessage,StoreMessage,QueueMessage,ResponseHandler,RenderResponse,UpdateHistory,Ready,UI frontend
    class StreamingInit,LiveQueue,ExtractFields,CheckStatus,GenerateMissing,GenerateSummary,ResponseStream,Budget,Size,PropType,City,ExtraFields backend
    class RootAgent,ExtractorAgent,ValidatorAgent agent
    class InitForm,UpdateForm,Validate,StatusUpdate,AdditionalFields,CheckComplete state
    class IsComplete decision

```
© 2025 [Nicolás Mateoli]. Todos los derechos reservados.
Este software es propiedad de Nicolás Mateoli.
No está permitida su reproducción, distribución o modificación sin autorización expresa.
---
