# 🚀 COI Compliance Pipeline - Quick Start Guide

## Production Deployment Options

### Option 1: Docker (Recommended)

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or run production container directly
docker build -t coi-compliance-pipeline .
docker run -p 5000:5000 --env-file .env coi-compliance-pipeline
```

### Option 2: Direct Python Execution

```bash
# Install dependencies
pip install -r requirements.txt

# Run the pipeline
python main.py

# Run with custom parameters
python main.py --data-path ./data --output-path ./reports --log-level INFO

# Run Flask API server
python app.py
```

### Option 3: Development Mode

```bash
# Run development server
docker-compose up coi-pipeline-dev

# Or run Flask in debug mode
FLASK_ENV=development FLASK_DEBUG=True python app.py
```

## API Endpoints

### Health Check
```bash
curl http://localhost:5000/health
```

### Document Analysis
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "document_text": "Your COI document text here",
    "parsed_fields": {"policy_number": "ABC123"}
  }'
```

### Generate Summary
```bash
curl -X POST http://localhost:5000/summary \
  -H "Content-Type: application/json" \
  -d '{
    "document_text": "Your COI document text here",
    "compliance_results": {"status": "compliant"}
  }'
```

## Configuration

### Environment Variables
- `GEMINI_API_KEY` - Your Google Gemini API key
- `FLASK_ENV` - Environment (development/production)
- `FLASK_DEBUG` - Debug mode (True/False)
- `LOG_LEVEL` - Logging level (DEBUG/INFO/WARNING/ERROR)

### Command Line Options
```bash
python main.py --help
```

## Monitoring

- **Health Check**: `GET /health`
- **Logs**: Check `logs/pipeline.log`
- **Metrics**: Available via Docker container stats

## File Structure

```
├── main.py              # Main entry point
├── app.py               # Flask API server
├── config.py            # Configuration management
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Multi-container setup
├── data/                # Input documents
├── reports/             # Generated reports
├── pipelines/           # ZenML pipeline definitions
├── steps/               # Individual pipeline steps
└── utils/               # Utility modules
```

## Production Checklist

- ✅ Environment variables configured
- ✅ Docker containers running
- ✅ Health endpoint responding
- ✅ Logs being written
- ✅ API endpoints accessible
- ✅ Gemini API key valid
- ✅ Reports directory writable

## Troubleshooting

### Common Issues

1. **API Key Invalid**: Check `GEMINI_API_KEY` in `.env`
2. **Port Already in Use**: Change port in `docker-compose.yml`
3. **Permission Errors**: Ensure Docker has access to directories
4. **Missing Dependencies**: Run `pip install -r requirements.txt`

### Debug Mode

```bash
# Enable debug logging
python main.py --log-level DEBUG

# Check health status
curl http://localhost:5000/health
```

## Support

For issues and contributions, visit: https://github.com/harshbopaliya/coi-compliance-zenml
