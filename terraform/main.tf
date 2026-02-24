# terraform\main.tf

############################################
# Terraform + Provider
############################################

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

############################################
# VARIABLES
############################################

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "Primary region"
  type        = string
}

variable "environment" {
  description = "Environment name (dev/staging/prod)"
  type        = string
}

variable "prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "labels" {
  description = "Common labels"
  type        = map(string)
  default     = {}
}

# --------------------------
# Artifact Registry
# --------------------------

variable "artifact_format" {
  description = "Artifact format (DOCKER, MAVEN, etc.)"
  type        = string
  default     = "DOCKER"
}

variable "artifact_description" {
  description = "Artifact repository description"
  type        = string
  default     = "Artifact repository"
}

# --------------------------
# BigQuery
# --------------------------

variable "dataset_id" {
  description = "BigQuery dataset ID"
  type        = string
}

variable "table_id" {
  description = "BigQuery table ID"
  type        = string
}

variable "dataset_location" {
  description = "BigQuery dataset location"
  type        = string
}

variable "dataset_delete_on_destroy" {
  description = "Allow dataset deletion"
  type        = bool
  default     = false
}

variable "table_schema" {
  description = "BigQuery table schema"
  type        = any
}

# --------------------------
# GCS
# --------------------------

variable "bucket_storage_class" {
  description = "GCS storage class"
  type        = string
  default     = "STANDARD"
}

variable "bucket_force_destroy" {
  description = "Force destroy buckets"
  type        = bool
  default     = false
}

variable "artifacts_retention_days" {
  description = "Retention days for artifacts bucket"
  type        = number
  default     = 30
}

variable "data_retention_days" {
  description = "Retention days for data bucket"
  type        = number
  default     = 7
}

# --------------------------
# IAM
# --------------------------

variable "cicd_roles" {
  description = "Roles for CI/CD service account"
  type        = list(string)
  default = [
    "roles/storage.objectAdmin",
    "roles/artifactregistry.writer"
  ]
}

variable "runtime_roles" {
  description = "Roles for runtime service account"
  type        = list(string)
  default = [
    "roles/storage.objectViewer"
  ]
}

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


############################################
# ARTIFACT REGISTRY
############################################

resource "google_artifact_registry_repository" "repo" {
  location      = var.region
  repository_id = "${var.prefix}-${var.environment}-repo"
  description   = var.artifact_description
  format        = var.artifact_format
  labels        = var.labels
}

############################################
# BIGQUERY
############################################

resource "google_bigquery_dataset" "dataset" {
  dataset_id                 = var.dataset_id
  location                   = var.dataset_location
  delete_contents_on_destroy = var.dataset_delete_on_destroy
  labels                     = var.labels
}

resource "google_bigquery_table" "table" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = var.table_id
  project    = var.project_id

  deletion_protection = false
  schema              = jsonencode(var.table_schema)

  labels = var.labels
}

############################################
# GCS BUCKETS
############################################

resource "google_storage_bucket" "artifacts" {
  name                        = "${var.prefix}-${var.environment}-artifacts-${var.project_id}"
  location                    = var.region
  storage_class               = var.bucket_storage_class
  force_destroy               = var.bucket_force_destroy
  uniform_bucket_level_access = true
  labels                      = var.labels

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = var.artifacts_retention_days
    }
  }
}

resource "google_storage_bucket" "data" {
  name                        = "${var.prefix}-${var.environment}-data-${var.project_id}"
  location                    = var.region
  storage_class               = var.bucket_storage_class
  force_destroy               = var.bucket_force_destroy
  uniform_bucket_level_access = true
  labels                      = var.labels

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = var.data_retention_days
    }
  }
}

############################################
# IAM
############################################

resource "google_service_account" "cicd" {
  account_id   = "${var.prefix}-${var.environment}-cicd"
  display_name = "CI/CD SA (${var.environment})"
}

resource "google_service_account" "runtime" {
  account_id   = "${var.prefix}-${var.environment}-runtime"
  display_name = "Runtime SA (${var.environment})"
}

resource "google_project_iam_member" "cicd_roles" {
  for_each = toset(var.cicd_roles)

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.cicd.email}"
}

resource "google_project_iam_member" "runtime_roles" {
  for_each = toset(var.runtime_roles)

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.runtime.email}"
}

############################################
# OUTPUTS
############################################

output "artifact_repo_url" {
  value = "${google_artifact_registry_repository.repo.location}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.repo.repository_id}"
}

output "artifacts_bucket" {
  value = google_storage_bucket.artifacts.name
}

output "data_bucket" {
  value = google_storage_bucket.data.name
}

output "dataset_id" {
  value = google_bigquery_dataset.dataset.dataset_id
}

output "cicd_service_account" {
  value = google_service_account.cicd.email
}

output "runtime_service_account" {
  value = google_service_account.runtime.email
}

