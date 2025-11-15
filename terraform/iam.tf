# Service account for backend Cloud Run service
resource "google_service_account" "backend_sa" {
  account_id   = "sm-ai-agency-backend"
  display_name = "Social Media AI Agency Backend Service Account"

  depends_on = [time_sleep.wait_for_apis]
}

# Grant Vertex AI User role (for Gemini, Veo)
resource "google_project_iam_member" "backend_vertex_ai" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.backend_sa.email}"
}

# Grant Storage Admin role (for video uploads)
resource "google_project_iam_member" "backend_storage" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.backend_sa.email}"
}

# Grant Secret Manager Accessor role
resource "google_project_iam_member" "backend_secrets" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.backend_sa.email}"
}

# Service account for frontend Cloud Run service
resource "google_service_account" "frontend_sa" {
  account_id   = "sm-ai-agency-frontend"
  display_name = "Social Media AI Agency Frontend Service Account"

  depends_on = [time_sleep.wait_for_apis]
}

# Output service account emails
output "backend_service_account_email" {
  value = google_service_account.backend_sa.email
}

output "frontend_service_account_email" {
  value = google_service_account.frontend_sa.email
}
