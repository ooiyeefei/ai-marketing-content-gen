# Cloud Storage bucket for generated videos and content
resource "google_storage_bucket" "content_bucket" {
  name          = "${var.project_id}-${var.app_name}-content"
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true

  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD"]
    response_header = ["*"]
    max_age_seconds = 3600
  }

  depends_on = [time_sleep.wait_for_apis]
}

# Make bucket publicly readable (for video serving)
resource "google_storage_bucket_iam_member" "public_read" {
  bucket = google_storage_bucket.content_bucket.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

# Output the bucket name
output "content_bucket_name" {
  value       = google_storage_bucket.content_bucket.name
  description = "Cloud Storage bucket for generated content"
}
