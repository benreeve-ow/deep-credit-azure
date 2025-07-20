# Azure Deployment Guide

This guide will help you deploy your OpenAI Responses API to Azure with Cosmos DB integration.

## Prerequisites

✅ **Azure Resources Already Created:**
- Azure App Service: `deep-credit-py-api` (North Europe)
- Azure Cosmos DB: `cosmos-deepcredit` (North Europe)
- Database: `deep-credit`
- Container: `reports_current`

## Step 1: Configure Azure App Service

### 1.1 Set Application Settings

In your Azure App Service (`deep-credit-py-api`), go to **Configuration** > **Application settings** and add these environment variables:

#### Required Settings:
```
OPENAI_API_KEY = your-openai-api-key-here
COSMOS_CONN = AccountEndpoint=https://cosmos-deepcredit.documents.azure.com:443/;AccountKey=your-cosmos-key==;
SECRET_KEY = your-flask-secret-key-here
```

#### Optional Settings:
```
WEBHOOK_TOKEN = your-secure-webhook-token-here
FLASK_ENV = production
WEBSITES_PORT = 8000
```

### 1.2 Generate Flask Secret Key

Run this command to generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 1.3 Get Cosmos DB Connection String

1. Go to your Cosmos DB account `cosmos-deepcredit` in Azure Portal
2. Navigate to **Keys** in the left sidebar
3. Copy the **Primary Connection String**
4. Replace the placeholder in `COSMOS_CONN` with your actual connection string

**Your Cosmos DB endpoint:** `https://cosmos-deepcredit.documents.azure.com:443/`

## Step 2: Cosmos DB Configuration

### 2.1 Existing Structure

The application is configured to work with your existing setup:
- **Database**: `deep-credit`
- **Container**: `reports_current`
- **Document Type**: `openai_response` (to distinguish from other documents)

### 2.2 Container Configuration

Your `reports_current` container is already set up. The application will:
- Store OpenAI responses with `type: "openai_response"`
- Use `run_id` as the document ID
- Add timestamps and metadata automatically

## Step 3: Update OpenAI Webhook Configuration

### 3.1 Production Webhook URL

Once deployed, your webhook URL will be:
```
https://deep-credit-py-api-ajawgjb7btc8enhe.northeurope-01.azurewebsites.net/webhook
```

### 3.2 Configure in OpenAI Dashboard

1. Go to your OpenAI dashboard
2. Navigate to webhook settings
3. Update the webhook URL to your Azure App Service URL
4. Set the webhook secret to match your `WEBHOOK_TOKEN`

## Step 4: Deploy via GitHub Actions

### 4.1 GitHub Secrets

Your GitHub Actions workflow is already configured. Make sure these secrets are set in your GitHub repository:

1. Go to your GitHub repository
2. Navigate to **Settings** > **Secrets and variables** > **Actions**
3. Verify these secrets exist:
   - `AZUREAPPSERVICE_CLIENTID_BD717A1751A549E7A3C92E591F548802`
   - `AZUREAPPSERVICE_TENANTID_CBAF68D3F6284CE49B7ED5F51F1A3488`
   - `AZUREAPPSERVICE_SUBSCRIPTIONID_487545CCFB2945A882BA4FC50FFDB01A`

### 4.2 Trigger Deployment

1. Push your changes to the `main` branch
2. The GitHub Actions workflow will automatically:
   - Build the application
   - Install dependencies
   - Deploy to Azure App Service

## Step 5: Verify Deployment

### 5.1 Check Application Status

Visit your Azure App Service URL:
```
https://deep-credit-py-api-ajawgjb7btc8enhe.northeurope-01.azurewebsites.net/api/status
```

You should see a response like:
```json
{
  "status": "running",
  "message": "OpenAI Responses API Test App",
  "environment": {
    "cosmos_db_configured": true,
    "openai_key_configured": true
  },
  "database": {
    "total_responses": 0,
    "database_name": "deep-credit",
    "container_name": "reports_current"
  }
}
```

### 5.2 Test the Application

1. **Web Interface**: Visit `https://deep-credit-py-api-ajawgjb7btc8enhe.northeurope-01.azurewebsites.net/`
2. **API Endpoints**: Test the various endpoints
3. **Database**: Check that responses are being stored in Cosmos DB

## Step 6: Monitoring and Troubleshooting

### 6.1 Application Logs

View logs in Azure Portal:
1. Go to your App Service `deep-credit-py-api`
2. Navigate to **Log stream** to see real-time logs
3. Check **Logs** for detailed application logs

### 6.2 Cosmos DB Monitoring

1. Go to your Cosmos DB account `cosmos-deepcredit`
2. Check **Metrics** for:
   - Request units consumed
   - Data usage
   - Throughput

### 6.3 Common Issues

#### Issue: "No Cosmos DB connection string found"
**Solution**: Ensure `COSMOS_CONN` is set in App Service Configuration

#### Issue: "Failed to initialize Cosmos DB connection"
**Solution**: 
1. Check the connection string format
2. Verify the Cosmos DB account is accessible
3. Check network security settings

#### Issue: "Webhook signature verification failed"
**Solution**: 
1. Ensure `WEBHOOK_TOKEN` matches the secret in OpenAI dashboard
2. Verify the webhook URL is correct

## Step 7: Production Considerations

### 7.1 Security

- ✅ Use HTTPS (enabled by default in Azure App Service)
- ✅ Store secrets in Azure Key Vault (recommended for production)
- ✅ Enable authentication if needed
- ✅ Configure CORS if required

### 7.2 Performance

- ✅ Monitor Cosmos DB RU consumption
- ✅ Set up auto-scaling if needed
- ✅ Use Application Insights for monitoring
- ✅ Configure CDN for static files if needed

### 7.3 Backup and Recovery

- ✅ Enable Cosmos DB automatic backups
- ✅ Set up App Service backup if needed
- ✅ Document recovery procedures

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `OPENAI_API_KEY` | Yes | Your OpenAI API key | `sk-...` |
| `COSMOS_CONN` | Yes | Cosmos DB connection string | `AccountEndpoint=https://cosmos-deepcredit.documents.azure.com:443/;AccountKey=...` |
| `SECRET_KEY` | Yes | Flask secret key | `abc123...` |
| `WEBHOOK_TOKEN` | No | Webhook security token | `your-token` |
| `FLASK_ENV` | No | Flask environment | `production` |
| `WEBSITES_PORT` | No | App Service port | `8000` |

## Your Azure Resources

- **App Service**: `deep-credit-py-api-ajawgjb7btc8enhe.northeurope-01.azurewebsites.net`
- **Cosmos DB**: `cosmos-deepcredit.documents.azure.com`
- **Database**: `deep-credit`
- **Container**: `reports_current`
- **Resource Group**: `ow-037-qiai_dev`
- **Region**: North Europe

## Support

If you encounter issues:

1. Check the application logs in Azure Portal
2. Verify all environment variables are set correctly
3. Test the Cosmos DB connection
4. Check the GitHub Actions deployment logs

## Next Steps

After successful deployment:

1. Set up monitoring with Application Insights
2. Configure custom domain if needed
3. Set up CI/CD for other environments (staging, etc.)
4. Implement additional security measures
5. Set up automated backups 