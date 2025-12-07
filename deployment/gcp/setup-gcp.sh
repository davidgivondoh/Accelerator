#!/bin/bash
# ==============================================================================
# Growth Engine - GCP Setup Script
# ==============================================================================
# This script sets up all required GCP resources for the Growth Engine
# Run with: ./setup-gcp.sh <PROJECT_ID> <REGION>
#
# Prerequisites:
# - gcloud CLI installed and authenticated
# - Appropriate IAM permissions
# ==============================================================================

set -e

# Configuration
PROJECT_ID="${1:-growth-engine-prod}"
REGION="${2:-us-central1}"
SERVICE_NAME="growth-engine"

echo "=========================================="
echo "Growth Engine GCP Setup"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "=========================================="

# Enable required APIs
echo "📦 Enabling required APIs..."
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    cloudscheduler.googleapis.com \
    secretmanager.googleapis.com \
    containerregistry.googleapis.com \
    cloudresourcemanager.googleapis.com \
    iam.googleapis.com \
    monitoring.googleapis.com \
    logging.googleapis.com \
    --project=$PROJECT_ID

echo "✓ APIs enabled"

# Create service accounts
echo "👤 Creating service accounts..."

# Main service account
gcloud iam service-accounts create growth-engine-sa \
    --display-name="Growth Engine Service Account" \
    --project=$PROJECT_ID 2>/dev/null || echo "Service account already exists"

# Scheduler service account
gcloud iam service-accounts create growth-engine-scheduler-sa \
    --display-name="Growth Engine Scheduler Service Account" \
    --project=$PROJECT_ID 2>/dev/null || echo "Scheduler service account already exists"

echo "✓ Service accounts created"

# Assign IAM roles
echo "🔐 Assigning IAM roles..."

# Main service account roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:growth-engine-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:growth-engine-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/logging.logWriter" \
    --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:growth-engine-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/monitoring.metricWriter" \
    --quiet

# Scheduler service account roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:growth-engine-scheduler-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/run.invoker" \
    --quiet

echo "✓ IAM roles assigned"

# Create secrets (placeholder - user needs to update values)
echo "🔑 Creating secrets..."

create_secret() {
    SECRET_NAME=$1
    PLACEHOLDER=$2
    
    if ! gcloud secrets describe $SECRET_NAME --project=$PROJECT_ID &>/dev/null; then
        echo "$PLACEHOLDER" | gcloud secrets create $SECRET_NAME \
            --data-file=- \
            --replication-policy="automatic" \
            --project=$PROJECT_ID
        echo "  Created secret: $SECRET_NAME (UPDATE WITH REAL VALUE!)"
    else
        echo "  Secret exists: $SECRET_NAME"
    fi
}

create_secret "database-url" "postgresql://user:password@host:5432/dbname"
create_secret "google-api-key" "your-google-api-key"
create_secret "anthropic-api-key" "your-anthropic-api-key"
create_secret "openai-api-key" "your-openai-api-key"
create_secret "pinecone-api-key" "your-pinecone-api-key"
create_secret "slack-webhook-url" "https://hooks.slack.com/services/xxx"

echo "✓ Secrets created (remember to update with real values!)"

# Create Cloud Build trigger
echo "🔨 Setting up Cloud Build..."

# Note: Cloud Build trigger should be created via Console or API
# as it requires repository connection
echo "  ⚠️  Create Cloud Build trigger manually in Console"
echo "     Connect your GitHub repository and use cloudbuild.yaml"

# Set up Cloud Scheduler jobs
echo "⏰ Creating Cloud Scheduler jobs..."

# Get Cloud Run URL (will be set after first deployment)
CLOUD_RUN_URL="https://${SERVICE_NAME}-xxxxx-uc.a.run.app"

echo "  ⚠️  Update cloud-scheduler-jobs.yaml with actual Cloud Run URL after deployment"
echo "     Then run: gcloud scheduler jobs create http ... for each job"

# Create monitoring dashboard
echo "📊 Setting up monitoring..."

cat > /tmp/growth-engine-dashboard.json << 'EOF'
{
  "displayName": "Growth Engine Dashboard",
  "gridLayout": {
    "columns": "2",
    "widgets": [
      {
        "title": "Request Count",
        "xyChart": {
          "dataSets": [{
            "timeSeriesQuery": {
              "timeSeriesFilter": {
                "filter": "resource.type=\"cloud_run_revision\" resource.label.service_name=\"growth-engine\"",
                "aggregation": {
                  "alignmentPeriod": "60s",
                  "perSeriesAligner": "ALIGN_RATE"
                }
              }
            }
          }]
        }
      },
      {
        "title": "Response Latency",
        "xyChart": {
          "dataSets": [{
            "timeSeriesQuery": {
              "timeSeriesFilter": {
                "filter": "resource.type=\"cloud_run_revision\" metric.type=\"run.googleapis.com/request_latencies\"",
                "aggregation": {
                  "alignmentPeriod": "60s",
                  "perSeriesAligner": "ALIGN_PERCENTILE_99"
                }
              }
            }
          }]
        }
      }
    ]
  }
}
EOF

gcloud monitoring dashboards create \
    --config-from-file=/tmp/growth-engine-dashboard.json \
    --project=$PROJECT_ID 2>/dev/null || echo "Dashboard may already exist"

echo "✓ Monitoring dashboard created"

# Create alerting policies
echo "🚨 Setting up alerting..."

cat > /tmp/error-rate-alert.json << 'EOF'
{
  "displayName": "Growth Engine - High Error Rate",
  "conditions": [{
    "displayName": "Error rate > 5%",
    "conditionThreshold": {
      "filter": "resource.type=\"cloud_run_revision\" resource.label.service_name=\"growth-engine\" metric.type=\"run.googleapis.com/request_count\" metric.label.response_code_class!=\"2xx\"",
      "aggregations": [{
        "alignmentPeriod": "300s",
        "perSeriesAligner": "ALIGN_RATE"
      }],
      "comparison": "COMPARISON_GT",
      "thresholdValue": 0.05,
      "duration": "300s"
    }
  }],
  "combiner": "OR",
  "enabled": true
}
EOF

echo "  ⚠️  Create alerting policies manually or via API"

# Summary
echo ""
echo "=========================================="
echo "✅ GCP Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Update secrets with real values:"
echo "   gcloud secrets versions add SECRET_NAME --data-file=secret.txt"
echo ""
echo "2. Connect GitHub repository to Cloud Build"
echo ""
echo "3. Deploy manually first time:"
echo "   gcloud builds submit --config=deployment/gcp/cloudbuild.yaml"
echo ""
echo "4. Get Cloud Run URL and update scheduler jobs:"
echo "   gcloud run services describe growth-engine --region=$REGION --format='value(status.url)'"
echo ""
echo "5. Create Cloud Scheduler jobs with the URL"
echo ""
echo "=========================================="
