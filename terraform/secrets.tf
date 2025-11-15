# Secret for Google Maps API key
resource "google_secret_manager_secret" "maps_api_key" {
  secret_id = "${var.app_name}-maps-api-key"

  replication {
    auto {}
  }

  depends_on = [time_sleep.wait_for_apis]
}

# Add secret version with the API key
resource "google_secret_manager_secret_version" "maps_api_key_version" {
  secret      = google_secret_manager_secret.maps_api_key.id
  secret_data = var.google_maps_api_key
}

# Grant backend service account access to secret
resource "google_secret_manager_secret_iam_member" "backend_maps_access" {
  secret_id = google_secret_manager_secret.maps_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.backend_sa.email}"
}

# Output secret name
output "maps_api_key_secret_name" {
  value = google_secret_manager_secret.maps_api_key.id
}
