# WhatsApp Automation Backend System

A comprehensive FastAPI backend system for WhatsApp automation with AI-powered chat responses, document management, and team collaboration features.

## Features

### Core System Architecture
- **FastAPI backend** with MongoDB Atlas for data storage
- **WhatsApp Web integration** via Node.js server webhooks
- **OpenAI integration** for AI-powered chat responses
- **MongoDB Atlas Vector Search** for document storage and RAG
- **JWT authentication** and workspace management

### Key Features
1. **Authentication System**
   - Email-based login/register
   - JWT token authentication
   - Admin and team member role management

2. **Workspace Management**
   - Create/manage multiple workspaces
   - Isolated data per workspace (users, phones, customers, knowledge base)
   - Admin can grant workspace access to team members

3. **WhatsApp Integration**
   - Webhook endpoints for QR codes from Node.js server
   - Phone number registration (max 2 per workspace)
   - Real-time message handling
   - Connection status management

4. **AI Chat System**
   - OpenAI integration with conversation memory
   - Configurable AI workflow steps per workspace
   - Toggle AI on/off for individual chats
   - Customizable prompt settings per workspace
   - Lead qualification based on workflow completion

5. **Chat Management**
   - Real-time chat dashboard
   - All conversations stored in MongoDB
   - Qualified/unqualified lead separation
   - Chat summary generation
   - Manual message sending when AI is disabled

6. **Knowledge Base**
   - Document upload (PDF, DOCX, TXT, Excel XLSX/XLS)
   - MongoDB Atlas Vector Search integration
   - OpenAI embedding model for processing
   - RAG (Retrieval Augmented Generation) implementation
   - Excel-specific processing with worksheet and table structure preservation

## Installation

### Prerequisites
- Python 3.8+
- MongoDB Atlas account
- OpenAI API key
- Node.js WhatsApp server (separate service)

### Backend Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd whatsapp-automation-backend
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Environment Configuration**
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=whatsapp_automation
SECRET_KEY=your-secret-key-change-this-in-production
OPENAI_API_KEY=your-openai-api-key-here
WHATSAPP_SERVER_URL=http://localhost:3000
```

4. **Start the backend server**
```bash
python -m app.main
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Install Node.js dependencies**
```bash
npm install
```

2. **Start the development server**
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## API Documentation

Once the server is running, you can access:
- **Interactive API docs**: `http://localhost:8000/docs`
- **ReDoc documentation**: `http://localhost:8000/redoc`

## Database Models

### Core Models
- **User**: Authentication and user management
- **Workspace**: Multi-tenant workspace system
- **Chat**: Customer conversations
- **Message**: Individual chat messages
- **Document**: Knowledge base documents
- **PhoneNumber**: WhatsApp phone number management
- **WorkflowStep**: AI workflow configuration

### Relationships
- Users can belong to multiple workspaces
- Workspaces contain isolated data (chats, documents, phones)
- Chats belong to specific workspaces and phone numbers
- Messages belong to chats
- Documents are workspace-specific with vector embeddings

## WhatsApp Integration

### Node.js Server Requirements
Your Node.js WhatsApp server should provide these endpoints:

1. **Send Message**
   - `POST /send-message`
   - Payload: `{ phone_number, to, message, type }`

2. **Connect Phone**
   - `POST /connect`
   - Payload: `{ phone_number, webhook_url }`
   - Returns: `{ qr_code }`

3. **Disconnect Phone**
   - `POST /disconnect`
   - Payload: `{ phone_number }`

4. **Status Check**
   - `GET /status/{phone_number}`
   - Returns: `{ status }`

### Webhook Endpoints
The backend provides these webhook endpoints for your Node.js server:

1. **Message Webhook**
   - `POST /webhooks/whatsapp/message`
   - Receives incoming WhatsApp messages

2. **Status Webhook**
   - `POST /webhooks/whatsapp/status`
   - Receives connection status updates

3. **Delivery Webhook**
   - `POST /webhooks/whatsapp/delivery`
   - Receives message delivery status

## AI Configuration

### OpenAI Integration
The system uses OpenAI for:
- **Chat responses**: GPT-3.5-turbo for conversational AI
- **Document embeddings**: text-embedding-ada-002 for vector search
- **Chat summaries**: Automated conversation summarization

### Workflow Configuration
Each workspace can define custom workflow steps:
- **Step description**: What the AI should accomplish
- **Required/optional**: Whether step completion is mandatory
- **Completion tracking**: Automatic progress monitoring
- **Lead qualification**: Based on workflow completion

## Security Features

### Authentication
- JWT token-based authentication
- Password hashing with bcrypt
- Token expiration and refresh

### Authorization
- Role-based access control (admin/member)
- Workspace-level permissions
- API rate limiting

### Data Security
- Input validation with Pydantic
- SQL injection prevention
- CORS configuration
- Request logging

## Deployment

### Production Deployment
1. **Environment Variables**
   - Set production MongoDB URL
   - Configure strong SECRET_KEY
   - Set OpenAI API key
   - Configure WhatsApp server URL

2. **Database Setup**
   - Create MongoDB Atlas cluster
   - Configure database indexes
   - Set up proper security rules

3. **Server Configuration**
   - Use production ASGI server (Gunicorn + Uvicorn)
   - Configure reverse proxy (Nginx)
   - Set up SSL certificates
   - Configure logging and monitoring

### Docker Deployment
```bash
docker build -t whatsapp-automation-backend .
docker run -p 8000:8000 --env-file .env whatsapp-automation-backend
```

## API Usage Examples

### Authentication
```bash
# Register new user
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123", "full_name": "John Doe"}'

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password123"
```

### Workspace Management
```bash
# Create workspace
curl -X POST "http://localhost:8000/workspaces" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Workspace", "description": "Test workspace"}'

# Get workspaces
curl -X GET "http://localhost:8000/workspaces" \
  -H "Authorization: Bearer <token>"
```

### Chat Operations
```bash
# Get workspace chats
curl -X GET "http://localhost:8000/chats/workspace/<workspace_id>" \
  -H "Authorization: Bearer <token>"

# Send message
curl -X POST "http://localhost:8000/chats/<chat_id>/messages" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello!", "direction": "outgoing"}'
```

## System Limitations

### Current Limitations
- Maximum 2 phone numbers per workspace
- File upload limited to 10MB
- Supports PDF, DOCX, TXT documents only
- Rate limiting: 100 requests per minute per IP

### Scaling Considerations
- Designed for 15-25 users
- Maximum 200 customer chats
- 3-10 workspaces maximum
- Simple UI optimized for small teams

## Support

For issues and support:
1. Check the API documentation at `/docs`
2. Review the logs for error details
3. Ensure all environment variables are set correctly
4. Verify MongoDB and OpenAI connectivity

## License

This project is licensed under the MIT License - see the LICENSE file for details.