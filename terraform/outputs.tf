# Service URLs
output "frontend_url" {
  value       = google_cloud_run_v2_service.frontend.uri
  description = "Frontend application URL"
}

output "backend_url" {
  value       = google_cloud_run_v2_service.backend.uri
  description = "Backend API URL"
}

# Instructions
output "deployment_complete" {
  value = <<-EOT

  ========================================
  DEPLOYMENT COMPLETE!
  ========================================

  Frontend URL: ${google_cloud_run_v2_service.frontend.uri}
  Backend URL:  ${google_cloud_run_v2_service.backend.uri}

  Content Bucket: ${google_storage_bucket.content_bucket.name}

  Next Steps:
  1. Open the frontend URL in your browser
  2. Enter a business website URL and address
  3. Generate 7 days of AI-powered social media content!

  ========================================
  EOT
  description = "Deployment summary and instructions"
}
