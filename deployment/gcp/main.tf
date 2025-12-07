# GCP Terraform Configuration for Growth Engine
# Infrastructure as Code for production deployment

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
  
  backend "gcs" {
    bucket = "growth-engine-terraform-state"
    prefix = "terraform/state"
  }
}

# ==============================================================================
# VARIABLES
# ==============================================================================

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "image_tag" {
  description = "Container image tag"
  type        = string
  default     = "latest"
}

# ==============================================================================
# PROVIDERS
# ==============================================================================

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# ==============================================================================
# SERVICE ACCOUNTS
# ==============================================================================

resource "google_service_account" "growth_engine" {
  account_id   = "growth-engine-sa"
  display_name = "Growth Engine Service Account"
  description  = "Service account for Growth Engine Cloud Run service"
}

resource "google_service_account" "scheduler" {
  account_id   = "growth-engine-scheduler-sa"
  display_name = "Growth Engine Scheduler Service Account"
  description  = "Service account for Cloud Scheduler jobs"
}

# IAM bindings for main service account
resource "google_project_iam_member" "growth_engine_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.growth_engine.email}"
}

resource "google_project_iam_member" "growth_engine_log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.growth_engine.email}"
}

resource "google_project_iam_member" "growth_engine_metric_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.growth_engine.email}"
}

# IAM binding for scheduler to invoke Cloud Run
resource "google_project_iam_member" "scheduler_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.scheduler.email}"
}

# ==============================================================================
# SECRETS
# ==============================================================================

resource "google_secret_manager_secret" "database_url" {
  secret_id = "database-url"
  
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "google_api_key" {
  secret_id = "google-api-key"
  
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "anthropic_api_key" {
  secret_id = "anthropic-api-key"
  
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "openai_api_key" {
  secret_id = "openai-api-key"
  
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "pinecone_api_key" {
  secret_id = "pinecone-api-key"
  
  replication {
    auto {}
  }
}

# Secret IAM access
resource "google_secret_manager_secret_iam_member" "growth_engine_database_url" {
  secret_id = google_secret_manager_secret.database_url.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.growth_engine.email}"
}

resource "google_secret_manager_secret_iam_member" "growth_engine_google_api" {
  secret_id = google_secret_manager_secret.google_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.growth_engine.email}"
}

resource "google_secret_manager_secret_iam_member" "growth_engine_anthropic_api" {
  secret_id = google_secret_manager_secret.anthropic_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.growth_engine.email}"
}

resource "google_secret_manager_secret_iam_member" "growth_engine_openai_api" {
  secret_id = google_secret_manager_secret.openai_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.growth_engine.email}"
}

resource "google_secret_manager_secret_iam_member" "growth_engine_pinecone_api" {
  secret_id = google_secret_manager_secret.pinecone_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.growth_engine.email}"
}

# ==============================================================================
# CLOUD RUN - API SERVICE
# ==============================================================================

resource "google_cloud_run_v2_service" "growth_engine" {
  name     = "growth-engine"
  location = var.region
  
  template {
    service_account = google_service_account.growth_engine.email
    
    scaling {
      min_instance_count = 1
      max_instance_count = 10
    }
    
    containers {
      image = "gcr.io/${var.project_id}/growth-engine:${var.image_tag}"
      
      ports {
        container_port = 8000
      }
      
      resources {
        limits = {
          cpu    = "2"
          memory = "2Gi"
        }
        cpu_idle = false
        startup_cpu_boost = true
      }
      
      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }
      
      env {
        name  = "LOG_LEVEL"
        value = "INFO"
      }
      
      env {
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.database_url.secret_id
            version = "latest"
          }
        }
      }
      
      env {
        name = "GOOGLE_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.google_api_key.secret_id
            version = "latest"
          }
        }
      }
      
      env {
        name = "ANTHROPIC_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.anthropic_api_key.secret_id
            version = "latest"
          }
        }
      }
      
      env {
        name = "OPENAI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.openai_api_key.secret_id
            version = "latest"
          }
        }
      }
      
      env {
        name = "PINECONE_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.pinecone_api_key.secret_id
            version = "latest"
          }
        }
      }
      
      startup_probe {
        http_get {
          path = "/health"
          port = 8000
        }
        initial_delay_seconds = 10
        period_seconds        = 10
        failure_threshold     = 3
      }
      
      liveness_probe {
        http_get {
          path = "/health"
          port = 8000
        }
        initial_delay_seconds = 15
        period_seconds        = 30
      }
    }
    
    timeout = "3600s"
    
    labels = {
      environment = var.environment
      app         = "growth-engine"
    }
  }
  
  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# Allow unauthenticated access (public API)
resource "google_cloud_run_service_iam_member" "public_access" {
  location = google_cloud_run_v2_service.growth_engine.location
  service  = google_cloud_run_v2_service.growth_engine.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ==============================================================================
# CLOUD RUN - SCHEDULER SERVICE
# ==============================================================================

resource "google_cloud_run_v2_service" "scheduler" {
  name     = "growth-engine-scheduler"
  location = var.region
  
  template {
    service_account = google_service_account.growth_engine.email
    
    scaling {
      min_instance_count = 0
      max_instance_count = 1
    }
    
    containers {
      image   = "gcr.io/${var.project_id}/growth-engine:${var.image_tag}"
      command = ["python", "-m", "src.scheduler"]
      
      resources {
        limits = {
          cpu    = "1"
          memory = "1Gi"
        }
      }
      
      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }
      
      env {
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.database_url.secret_id
            version = "latest"
          }
        }
      }
      
      env {
        name = "GOOGLE_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.google_api_key.secret_id
            version = "latest"
          }
        }
      }
    }
  }
}

# ==============================================================================
# CLOUD SCHEDULER JOBS
# ==============================================================================

resource "google_cloud_scheduler_job" "daily_discovery" {
  name        = "growth-engine-daily-discovery"
  description = "Daily opportunity discovery job"
  schedule    = "0 6 * * *"
  time_zone   = "UTC"
  
  retry_config {
    retry_count = 3
  }
  
  http_target {
    uri         = "${google_cloud_run_v2_service.growth_engine.uri}/api/v1/discovery/run"
    http_method = "POST"
    
    headers = {
      "Content-Type" = "application/json"
    }
    
    body = base64encode(jsonencode({
      sources        = ["linkedin", "angelist", "ycombinator", "wellfound"]
      max_per_source = 25
      min_fit_score  = 0.7
    }))
    
    oidc_token {
      service_account_email = google_service_account.scheduler.email
    }
  }
}

resource "google_cloud_scheduler_job" "evening_applications" {
  name        = "growth-engine-evening-applications"
  description = "Evening application generation job"
  schedule    = "0 19 * * 1-5"
  time_zone   = "UTC"
  
  retry_config {
    retry_count = 2
  }
  
  http_target {
    uri         = "${google_cloud_run_v2_service.growth_engine.uri}/api/v1/applications/generate-batch"
    http_method = "POST"
    
    headers = {
      "Content-Type" = "application/json"
    }
    
    body = base64encode(jsonencode({
      max_applications = 10
      require_approval = true
      min_fit_score    = 0.75
    }))
    
    oidc_token {
      service_account_email = google_service_account.scheduler.email
    }
  }
}

resource "google_cloud_scheduler_job" "weekly_analytics" {
  name        = "growth-engine-weekly-analytics"
  description = "Weekly analytics and reporting job"
  schedule    = "0 8 * * 0"
  time_zone   = "UTC"
  
  http_target {
    uri         = "${google_cloud_run_v2_service.growth_engine.uri}/api/v1/analytics/generate-report"
    http_method = "POST"
    
    headers = {
      "Content-Type" = "application/json"
    }
    
    body = base64encode(jsonencode({
      report_type             = "weekly"
      include_recommendations = true
      send_email              = true
    }))
    
    oidc_token {
      service_account_email = google_service_account.scheduler.email
    }
  }
}

resource "google_cloud_scheduler_job" "health_check" {
  name        = "growth-engine-health-check"
  description = "Hourly system health check"
  schedule    = "0 * * * *"
  time_zone   = "UTC"
  
  http_target {
    uri         = "${google_cloud_run_v2_service.growth_engine.uri}/health"
    http_method = "GET"
    
    oidc_token {
      service_account_email = google_service_account.scheduler.email
    }
  }
}

# ==============================================================================
# MONITORING
# ==============================================================================

resource "google_monitoring_alert_policy" "error_rate" {
  display_name = "Growth Engine - High Error Rate"
  combiner     = "OR"
  
  conditions {
    display_name = "Error rate > 5%"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.label.service_name=\"growth-engine\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.label.response_code_class!=\"2xx\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.05
      
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }
  
  notification_channels = []  # Add notification channel IDs
  
  alert_strategy {
    auto_close = "1800s"
  }
}

resource "google_monitoring_alert_policy" "latency" {
  display_name = "Growth Engine - High Latency"
  combiner     = "OR"
  
  conditions {
    display_name = "P99 latency > 10s"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.label.service_name=\"growth-engine\" AND metric.type=\"run.googleapis.com/request_latencies\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 10000  # 10 seconds in ms
      
      aggregations {
        alignment_period     = "300s"
        per_series_aligner   = "ALIGN_PERCENTILE_99"
      }
    }
  }
  
  notification_channels = []
}

# ==============================================================================
# OUTPUTS
# ==============================================================================

output "api_url" {
  description = "Growth Engine API URL"
  value       = google_cloud_run_v2_service.growth_engine.uri
}

output "scheduler_url" {
  description = "Scheduler service URL"
  value       = google_cloud_run_v2_service.scheduler.uri
}

output "service_account_email" {
  description = "Main service account email"
  value       = google_service_account.growth_engine.email
}

output "scheduler_service_account_email" {
  description = "Scheduler service account email"
  value       = google_service_account.scheduler.email
}
