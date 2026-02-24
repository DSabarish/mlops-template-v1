Good question — this is **core DevOps architecture**, especially for the kind of GCP Terraform + CI/CD project you’re building.

I’ll explain the **real-world industry pattern**, not tutorial style.

---

# Big picture

Terraform = *provision infrastructure*
CI/CD = *deploy application*

They are **separate pipelines that talk to each other**.

Think of it as:

```
Developer pushes code
        ↓
CI/CD pipeline runs
        ↓
Infra pipeline ensures infra exists
        ↓
App pipeline deploys into that infra
```

Terraform is never run manually in mature setups.
It is always triggered by CI/CD.

---

# The standard architecture

There are **two common patterns** used in companies.

---

## Pattern 1 — Separate Infra Pipeline (Most common / recommended)

This is what most companies do.

You keep **two repos or two pipelines**:

```
Repo 1 → terraform-infra
Repo 2 → application code
```

### Flow

```
Terraform Repo Pipeline
    → Creates GCP infra
        - VPC
        - GKE / Cloud Run
        - Service accounts
        - Artifact Registry
        - Secrets
        - Buckets
    → Outputs infra details

Application Repo Pipeline
    → Builds app
    → Pushes image to Artifact Registry
    → Deploys to Cloud Run / GKE using existing infra
```

### Why separation?

Because infra changes:

* are rare
* risky
* need approvals
* are managed by DevOps team

App deployments:

* happen many times per day
* owned by developers

So pipelines are split.

---

## How they are linked (important part)

They are linked using **remote state + outputs**.

Terraform produces outputs like:

```hcl
output "artifact_registry_repo" {
  value = google_artifact_registry_repository.repo.repository_id
}

output "cloud_run_service_name" {
  value = google_cloud_run_service.app.name
}
```

These outputs are stored in **Terraform Remote State** (GCS bucket).

Then the **App CI/CD pipeline reads this state**.

---

## The glue: Terraform Remote State (GCS)

Typical backend:

```hcl
terraform {
  backend "gcs" {
    bucket  = "my-tf-state-bucket"
    prefix  = "dev"
  }
}
```

This becomes the **single source of truth**.

---

## How CI/CD reads Terraform outputs

In Cloud Build / GitHub Actions / GitLab CI:

```bash
terraform output -json > tf_outputs.json
```

Example outputs:

```json
{
  "artifact_registry_repo": {
    "value": "iris-repo"
  },
  "cloud_run_service_name": {
    "value": "iris-api"
  }
}
```

Pipeline uses these values to deploy.

This is the *link* between Terraform and CI/CD.

---

# Real production workflow (step-by-step)

## Step 1 — Dev merges Terraform change

Trigger: push to `infra/dev` branch

Pipeline runs:

```
terraform init
terraform plan
(terraform plan approval step)
terraform apply
```

Result:
Infra exists in GCP.

---

## Step 2 — Dev merges app code

Trigger: push to `app/dev` branch

Pipeline runs:

1. Read Terraform outputs
2. Build container
3. Push image
4. Deploy to Cloud Run/GKE

Example:

```bash
REPO=$(terraform output -raw artifact_registry_repo)

docker build -t $REGION-docker.pkg.dev/$PROJECT/$REPO/app:$SHA .
docker push $REGION-docker.pkg.dev/$PROJECT/$REPO/app:$SHA

gcloud run deploy service-name \
  --image $REGION-docker.pkg.dev/$PROJECT/$REPO/app:$SHA
```

---

# How environments fit in (Dev / QA / Prod)

This is where Terraform shines.

Typical structure:

```
terraform/
  environments/
    dev/
    qa/
    prod/
```

Each environment has its own:

* state file
* service accounts
* pipelines
* secrets

CI/CD promotes code:

```
dev → qa → prod
```

Infra pipeline runs per environment.

---

# Where the service account fits

CI/CD pipeline uses a **Service Account created by Terraform**.

Terraform creates:

```
ci-cd-sa@project.iam.gserviceaccount.com
```

Pipeline authenticates using Workload Identity or key.

This is exactly what you were fixing yesterday with:

```
gcloud auth application-default login
```

You were basically connecting your local environment the same way the pipeline will.

---

# TL;DR (industry answer)

Terraform and CI/CD are linked by:

1. CI/CD triggers Terraform automatically
2. Terraform stores outputs in remote state
3. App pipeline reads Terraform outputs
4. App pipeline deploys into infra created by Terraform

**Terraform builds the house → CI/CD moves the furniture.**

---

If you want, next we can map this specifically to your **GCP + Terraform + Iris CI/CD project** and design the exact pipelines (Cloud Build vs GitHub Actions).
