#!/bin/bash
set -e

echo "🚀 GCP AI Monitor Deployment"

# Ask user for info
read -p "Enter your name: " USER_NAME
read -p "Enter your email: " USER_EMAIL
read -p "Enter GCP Project ID: " PROJECT_ID

# Create env.yaml for Cloud Function
cat > env.yaml <<EOF
USER_NAME: "$USER_NAME"
USER_EMAIL: "$USER_EMAIL"
GCP_PROJECT: "$PROJECT_ID"
GCP_REGION: "us-central1"
EOF

echo "✅ Environment file created:"
cat env.yaml

# Deploy Cloud Function
echo "Deploying Cloud Function..."
gcloud functions deploy monitor_gcp \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=monitor_gcp \
  --trigger-http \
  --allow-unauthenticated \
  --memory=512MB \
  --timeout=60s \
  --env-vars-file=env.yaml \
  --max-instances=1

echo "✅ Deployment complete!"
echo "You can now open the Cloud Function URL to see the interface."
