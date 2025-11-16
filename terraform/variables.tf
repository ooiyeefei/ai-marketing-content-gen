variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "veo-licious-gems"
}

variable "google_maps_api_key" {
  description = "Google Maps Places API key"
  type        = string
  sensitive   = true
}
