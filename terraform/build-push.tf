# Build and push frontend Docker image
resource "null_resource" "build_frontend_image" {
  depends_on = [google_artifact_registry_repository.docker_repo]

  triggers = {
    # Rebuild if source code changes
    source_hash = sha256(join("", [
      filesha256("${path.module}/../frontend/Dockerfile"),
      filesha256("${path.module}/../frontend/package.json"),
    ]))
  }

  provisioner "local-exec" {
    command = <<-EOT
      cd ${path.module}/../frontend

      # Build Docker image
      docker build \
        --platform linux/amd64 \
        -t ${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/frontend:latest \
        .

      # Configure Docker auth for Artifact Registry
      gcloud auth configure-docker ${var.region}-docker.pkg.dev --quiet

      # Push image
      docker push ${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/frontend:latest
    EOT
  }
}

# Build and push backend Docker image
resource "null_resource" "build_backend_image" {
  depends_on = [google_artifact_registry_repository.docker_repo]

  triggers = {
    # Rebuild if source code changes
    source_hash = sha256(join("", [
      filesha256("${path.module}/../backend/Dockerfile"),
      filesha256("${path.module}/../backend/requirements.txt"),
    ]))
  }

  provisioner "local-exec" {
    command = <<-EOT
      cd ${path.module}/../backend

      # Build Docker image
      docker build \
        --platform linux/amd64 \
        -t ${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/backend:latest \
        .

      # Configure Docker auth for Artifact Registry
      gcloud auth configure-docker ${var.region}-docker.pkg.dev --quiet

      # Push image
      docker push ${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/backend:latest
    EOT
  }
}

# Outputs
output "frontend_image" {
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/frontend:latest"
  description = "Frontend Docker image URI"
  depends_on  = [null_resource.build_frontend_image]
}

output "backend_image" {
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/backend:latest"
  description = "Backend Docker image URI"
  depends_on  = [null_resource.build_backend_image]
}
