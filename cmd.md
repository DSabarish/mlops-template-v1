############################################
# ✅ GOLDEN PATH — FULL EXECUTION SCRIPT
############################################

# -------------------------------
# 🔹 PROJECT VARIABLE
# -------------------------------
$PROJECT_ID = "dn-project-template"
echo $PROJECT_ID

# -------------------------------
# ✅ STEP 1 — Environment & Tools
# -------------------------------
terraform -version
gcloud version

# Clear any manually set credentials path
$env:GOOGLE_APPLICATION_CREDENTIALS=""

# -------------------------------
# ✅ STEP 2 — Authentication & Project Setup
# -------------------------------

# 1. Clear old sessions
gcloud auth application-default revoke

# 2. Login fresh
gcloud auth login
gcloud auth application-default login

# 3. Force focus to target project
gcloud config set project $PROJECT_ID
gcloud auth application-default set-quota-project $PROJECT_ID

# 4. Verification (The "Big Three")
gcloud auth list
gcloud config get-value project
cat $env:APPDATA\gcloud\application_default_credentials.json

# -------------------------------
# ✅ STEP 3 — Enable Required APIs
# -------------------------------_
gcloud services enable artifactregistry.googleapis.com --project $PROJECT_ID
gcloud services enable bigquery.googleapis.com --project $PROJECT_ID
gcloud services enable bigquery.googleapis.com --project $PROJECT_ID
gcloud services enable iam.googleapis.com --project $PROJECT_ID

# -------------------------------
# ✅ STEP 4 — Prepare Terraform
# -------------------------------

cd terraform

# Ensure dev.tfvars contains:
# project_id = "$PROJECT_ID"

# Wipe old state (prevents cross-project issues)
rm terraform.tfstate -ErrorAction SilentlyContinue
rm terraform.tfstate.backup -ErrorAction SilentlyContinue

# Fresh initialization
terraform init -reconfigure

# -------------------------------
# ✅ STEP 5 — Plan
# -------------------------------
terraform plan -var-file="dev.tfvars"

# Verify:
# - All resources show project = "$PROJECT_ID"
# - Plan summary looks correct

# -------------------------------
# ✅ STEP 6 — Apply
# -------------------------------
terraform apply -var-file="dev.tfvars"
# Type 'yes' when prompted

############################################
# ✅ DONE — INFRA DEPLOYED TO $PROJECT_ID
############################################


artifact_repo_url = "asia-south1-docker.pkg.dev/dn-project-template/sabs-dev-repo"
artifacts_bucket = "sabs-dev-artifacts-dn-project-template"
cicd_service_account = "sabs-dev-cicd@dn-project-template.iam.gserviceaccount.com"
data_bucket = "sabs-dev-data-dn-project-template"
dataset_id = "training_dataset_dev"
project_id = "dn-project-template"
runtime_service_account = "sabs-dev-runtime@dn-project-template.iam.gserviceaccount.com"
table_id = "features_table"