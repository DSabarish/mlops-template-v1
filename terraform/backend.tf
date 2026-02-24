# -----------------------------------------------------------------------------
# Remote state in GCS. Bucket and prefix are set in CI per environment:
#   -backend-config="bucket=YOUR_STATE_BUCKET" -backend-config="prefix=ENVIRONMENT"
# This keeps dev/qa/prod state isolated (separate prefix per environment).
# -----------------------------------------------------------------------------

terraform {
  backend "gcs" {
    # bucket = set via -backend-config in GitHub Actions
    # prefix = set via -backend-config (e.g. "dev", "qa", "prod")
  }
}
