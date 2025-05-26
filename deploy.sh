#!/bin/bash

# Set your project variables
PROJECT_ID="live-telebot-production"
SERVICE_NAME="telegram-bot"
REGION="asia-southeast-1"
TELE_TOKEN="7928950540:AAGGct7klfMLaMaJztDv7ZuFTeRKIiMKWIU"

# Set the GCP project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and deploy to Cloud Run
echo "🚀 Building and deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars="TELE_TOKEN=$TELE_TOKEN,JSON_PATHNAME=credentials.json" \
  --timeout 300

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
echo "🌐 Service deployed at: $SERVICE_URL"

# Set the webhook
echo "📡 Setting up Telegram webhook..."
curl -X POST "https://api.telegram.org/bot$TELE_TOKEN/setWebhook" \
  -d "url=$SERVICE_URL/$TELE_TOKEN"

echo "✅ Deployment complete!"
echo "🔗 Webhook URL: $SERVICE_URL/$TELE_TOKEN"