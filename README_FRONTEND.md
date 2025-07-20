# OpenAI Responses API Test App - Frontend

A modern, responsive web interface for testing OpenAI's Responses API with background processing and webhook support.

## 🚀 Features

### **Modern Web Interface**
- **Beautiful, responsive design** with gradient backgrounds and smooth animations
- **Real-time status updates** with spinning indicators and progress tracking
- **Query history** showing all previous requests and responses
- **Error handling** with user-friendly error messages
- **Mobile-friendly** responsive design

### **Background Processing**
- **Asynchronous queries** - no waiting for responses
- **Real-time polling** - automatic status updates every 2 seconds
- **Webhook integration** - receives notifications when responses complete
- **Dual system** - both polling and webhooks work together for reliability

### **Data Management**
- **Local storage** - all queries and responses stored in memory
- **History tracking** - complete audit trail of all requests
- **Status monitoring** - detailed progress information
- **Debug endpoint** - access to all stored data via API

## 🎯 How It Works

### **1. Query Submission**
1. Enter your query in the text input
2. Click "Send Query" or press Enter
3. The system submits the query to OpenAI in background mode
4. You get immediate feedback with a Run ID

### **2. Real-time Monitoring**
1. The interface shows a spinning indicator
2. Status updates every 2 seconds via polling
3. Webhooks provide instant notifications when complete
4. Progress details include OpenAI status and timestamps

### **3. Response Display**
1. When complete, the response appears in a dedicated section
2. Full response text with proper formatting
3. Completion timestamp and metadata
4. Automatic history refresh

### **4. Query History**
1. All queries are stored locally
2. History shows query, response preview, and metadata
3. Sorted by completion time (newest first)
4. Click on history items to view details

## 🛠️ Architecture

### **Frontend (index.html)**
- **Vanilla JavaScript** - no frameworks required
- **Modern CSS** - gradients, animations, responsive design
- **Fetch API** - for backend communication
- **Real-time updates** - polling and webhook integration

### **Backend (Flask)**
- **RESTful API** - clean endpoint design
- **Background processing** - OpenAI Responses API with `background=True`
- **Webhook handling** - secure signature verification
- **Local storage** - in-memory data management
- **Polling support** - automatic status checking

### **Data Flow**
```
User Input → Flask /start → OpenAI API (background) → Webhook/Polling → Response Display
```

## 📡 API Endpoints

### **Web Interface**
- `GET /` - Main web interface
- `GET /api/status` - API status information

### **Core API**
- `POST /start` - Start a new OpenAI response
- `GET /status/<run_id>` - Check response status
- `POST /webhook` - Receive webhook notifications
- `GET /debug` - View all stored data

## 🔧 Configuration

### **Environment Variables**
```bash
# Required
OPENAI_API_KEY=your-openai-api-key-here

# Optional (for webhook security)
WEBHOOK_TOKEN=your-webhook-secret-here
```

### **Webhook Setup**
1. Start ngrok: `ngrok http 8000`
2. Configure webhook in OpenAI dashboard: `https://your-ngrok-url.ngrok.io/webhook`
3. Add webhook secret to `.env` file

## 🎨 Design Features

### **Visual Design**
- **Gradient backgrounds** - modern purple/blue theme
- **Card-based layout** - clean, organized sections
- **Smooth animations** - hover effects and transitions
- **Responsive design** - works on all screen sizes

### **User Experience**
- **Real-time feedback** - immediate status updates
- **Error handling** - clear error messages
- **Loading states** - visual progress indicators
- **History management** - easy access to past queries

## 🚀 Getting Started

1. **Start the app:**
   ```bash
   ./start_app.sh
   ```

2. **Open your browser:**
   ```
   http://localhost:8000
   ```

3. **Enter a query:**
   - Type your question in the input field
   - Click "Send Query"
   - Watch the real-time progress
   - View the response when complete

4. **Explore history:**
   - Scroll down to see all previous queries
   - Click on history items for details

## 🔮 Future Enhancements

### **Planned Features**
- **Database integration** - Cosmos DB for persistent storage
- **User authentication** - secure access control
- **Advanced filtering** - search and filter history
- **Export functionality** - download responses as files
- **Collaboration features** - share queries and responses

### **Architecture Evolution**
- **Microservices** - separate frontend and backend
- **Message queues** - Redis/RabbitMQ for job management
- **Caching layer** - Redis for performance
- **Monitoring** - Prometheus/Grafana for metrics

## 🐛 Troubleshooting

### **Common Issues**
1. **No webhook signatures** - Check webhook configuration in OpenAI dashboard
2. **Polling errors** - Verify OpenAI API key is valid
3. **History not loading** - Check browser console for errors
4. **Responsive issues** - Ensure browser supports modern CSS

### **Debug Tools**
- **Browser console** - JavaScript errors and network requests
- **Flask logs** - Backend processing information
- **Debug endpoint** - `GET /debug` for data inspection
- **API status** - `GET /api/status` for system health

## 📚 Technical Details

### **Technologies Used**
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Backend:** Python Flask, OpenAI SDK
- **Styling:** Custom CSS with modern features
- **Communication:** Fetch API, WebSockets (future)

### **Security Features**
- **Webhook signature verification** - cryptographic validation
- **Input sanitization** - XSS protection
- **CORS handling** - cross-origin request management
- **Environment variable protection** - secure configuration

---

**Built with ❤️ for testing OpenAI's Responses API with modern web technologies.** 