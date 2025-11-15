# Enable required Google Cloud APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",                    # Cloud Run
    "artifactregistry.googleapis.com",       # Artifact Registry
    "cloudbuild.googleapis.com",             # Cloud Build (for Docker)
    "storage.googleapis.com",                # Cloud Storage
    "aiplatform.googleapis.com",             # Vertex AI (Gemini, Veo)
    "secretmanager.googleapis.com",          # Secret Manager
    "places-backend.googleapis.com",         # Places API
  ])

  project = var.project_id
  service = each.key

  disable_on_destroy = false
}

# Wait for APIs to be fully enabled
resource "time_sleep" "wait_for_apis" {
  depends_on = [google_project_service.required_apis]

  create_duration = "60s"
}
