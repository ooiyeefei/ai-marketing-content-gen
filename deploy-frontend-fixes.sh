#!/bin/bash
# Deploy frontend with UI visibility fixes

set -e

cd "$(dirname "$0")/frontend"

echo "Building frontend with UI fixes..."
docker build --platform linux/amd64 \
  -t us-central1-docker.pkg.dev/gen-lang-client-0375244352/social-media-ai-agency-images/frontend:latest \
  .

echo "Pushing to Artifact Registry..."
docker push us-central1-docker.pkg.dev/gen-lang-client-0375244352/social-media-ai-agency-images/frontend:latest

echo "Deploying to Cloud Run..."
gcloud run deploy social-media-ai-agency-frontend \
  --image us-central1-docker.pkg.dev/gen-lang-client-0375244352/social-media-ai-agency-images/frontend:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated

echo "✅ Frontend deployed successfully!"
echo "URL: https://social-media-ai-agency-frontend-131242460201.us-central1.run.app"
