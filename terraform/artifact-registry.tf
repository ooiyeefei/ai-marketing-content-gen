# Artifact Registry repository for Docker images
resource "google_artifact_registry_repository" "docker_repo" {
  location      = var.region
  repository_id = "${var.app_name}-images"
  description   = "Docker images for Social Media AI Agency"
  format        = "DOCKER"

  depends_on = [time_sleep.wait_for_apis]
}

# Output the repository URL
output "artifact_registry_url" {
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}"
  description = "Artifact Registry URL for Docker images"
}
