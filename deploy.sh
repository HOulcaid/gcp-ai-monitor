#!/bin/bash
set -e

echo "🚀 GCP AI Monitor Deployment Script"
echo "------------------------------------"

# Ask user for info
read -p "Enter your name: " USER_NAME
read -p "Enter your email: " USER_EMAIL
read -p "Enter GCP Project ID: " PROJECT_ID
read -p "Enter the email of the Service Account to use: " SA_EMAIL

# Set project
gcloud config set project $PROJECT_ID

# --- Enable Required Services ---
echo "🛠️  Enabling required Google Cloud services..."
gcloud services enable \
  cloudfunctions.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  iam.googleapis.com

echo "✅ Services enabled."

# --- IAM & Service Account Setup ---
echo "🛠️  Configuring IAM permissions for Service Account: ${SA_EMAIL}..."

# Validate Service Account exists
if ! gcloud iam service-accounts describe ${SA_EMAIL} >/dev/null 2>&1; then
  echo "❌ Error: Service Account '${SA_EMAIL}' not found in project '${PROJECT_ID}'."
  exit 1
fi
echo "✅ Service Account found."

# Grant necessary roles to the Service Account (e.g., Monitoring Viewer)
echo "Granting 'Monitoring Viewer' role to the Service Account..."
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/monitoring.viewer" \
  --condition=None >/dev/null # Suppress verbose output

# Grant the user deploying the function permission to act as the Service Account
DEPLOYING_USER=$(gcloud config get-value account)
echo "Granting 'Service Account User' role to deploying user (${DEPLOYING_USER})..."
gcloud iam service-accounts add-iam-policy-binding ${SA_EMAIL} \
    --member="user:${DEPLOYING_USER}" \
    --role="roles/iam.serviceAccountUser" >/dev/null # Suppress verbose output

echo "✅ IAM setup complete."

# Create env.yaml for Cloud Function
cat > env.yaml <<EOF
USER_NAME: "$USER_NAME"
USER_EMAIL: "$USER_EMAIL"
GCP_PROJECT: "$PROJECT_ID"
GCP_REGION: "us-central1"
EOF

echo "✅ Environment file created:"
cat env.yaml | sed 's/^/  /' # Indent for readability

# Deploy Cloud Function
echo "🚀 Deploying Cloud Function..."
gcloud functions deploy monitor_gcp \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=monitor_gcp \
  --trigger-http \
  --allow-unauthenticated \
  --service-account=${SA_EMAIL} \
  --memory=512MB \
  --timeout=60s \
  --env-vars-file=env.yaml \

echo "✅ Deployment complete!"
echo "You can now open the Cloud Function URL to see the interface."
