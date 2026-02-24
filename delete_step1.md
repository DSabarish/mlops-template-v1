
You’ve already pushed your code (including the workflow) to `dev`. Here’s how to **set up GitHub Actions** from here.

---

## Step 1: Add the required GitHub secrets

The workflow needs these in the repo so it can run (auth + state).

1. Open the repo: **https://github.com/DSabarish/infra-build-automation**
2. Go to **Settings → Secrets and variables → Actions**
3. Click **New repository secret** and add:

**If you use the OIDC workflow (terraform-deploy.yml):**

| Secret name           | Value |
|-----------------------|--------|
| `WIF_PROVIDER`        | Full WIF provider resource name, e.g. `projects/123456789/locations/global/workloadIdentityPools/github-pool/providers/github` |
| `WIF_SERVICE_ACCOUNT` | Terraform CI service account email, e.g. `terraform-ci@dn-project-template.iam.gserviceaccount.com` |
| `TF_STATE_BUCKET`     | Your GCS Terraform state bucket name, e.g. `dn-project-template-tfstate` |

**If you use the key-based workflow (terraform-infra.yml):**

| Secret name        | Value |
|--------------------|--------|
| `GCP_SA_KEY`       | Full contents of the JSON key file for your GCP service account |
| `TF_STATE_BUCKET`  | Your GCS Terraform state bucket name (optional; if set, remote state is used) |

Step 1 is: **add these secrets** (and create the GCP bits below if they don’t exist yet).

---

## Step 2: Create GCP resources (if not done yet)

- **State bucket:** In GCP Console → Cloud Storage → Create bucket (e.g. `dn-project-template-tfstate`). Note the name for `TF_STATE_BUCKET`.
- **Service account:** IAM → Service accounts → Create (e.g. `terraform-ci`). Grant it:
  - Access to the state bucket (e.g. Storage Object Admin),
  - Permissions to create/manage your Terraform resources (e.g. Editor or the roles your Terraform needs).
- **If using OIDC:** Set up Workload Identity Federation (pool + OIDC provider for GitHub), then grant that provider “Workload Identity User” on the service account. Use the pool/provider path and SA email for `WIF_PROVIDER` and `WIF_SERVICE_ACCOUNT`.
- **If using keys:** Create a JSON key for that service account and paste the whole file into `GCP_SA_KEY`.

---

## Step 3: Confirm the workflow is on `dev`

- In the repo, open **Actions**.
- Check that you see the workflow (e.g. “Terraform Deploy (GCP)” or “Terraform Infra”).
- Your workflow files live under `.github/workflows/`. As long as that folder was included in your `git push origin dev`, the workflow is already on `dev`.

---

## Step 4: Run it

- **Option A:** Push a commit that touches `terraform/**` or the workflow file (or open a PR into `main` if the workflow runs on PR).
- **Option B:** In **Actions**, open the workflow and click **Run workflow**, choose branch `dev` (or `main` if that’s what the workflow uses), then Run.

---

**Summary:** Step 1 is **add the GitHub secrets** (and create the GCP state bucket + service account + WIF or key if you haven’t already). After that, the workflow can run when you push or trigger it from the Actions tab.