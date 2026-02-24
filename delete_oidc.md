You’re hitting an org‑level security guardrail:

> **Service account key creation is disabled** (org policy `iam.disableServiceAccountKeyCreation`)

So you **cannot** get a JSON key → **`GCP_SA_KEY` is not an option in this org.**  
The correct path is to use **Workload Identity Federation (OIDC)** only (no keys).

Below is what you need to do, step‑by‑step, without changing any code yet.

---

### 1. High‑level: what changes

- **Stop trying to create/download keys** → no `GCP_SA_KEY`.
- **Use OIDC from GitHub to GCP** via `google-github-actions/auth@v2` with:
  - `workload_identity_provider`: your WIF provider resource name
  - `service_account`: the email of a GCP service account that Terraform will impersonate

Your Terraform workflow will look like:

```yaml
- name: Authenticate to GCP
  uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
    service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
```

No `credentials_json` and no key secrets.

---

### 2. GCP setup (one time)

In the **same project** where Terraform runs:

1. **Create / pick a service account**  
   - IAM & Admin → Service accounts → Create (e.g. `terraform-ci`).  
   - Grant it the roles Terraform needs (Storage Admin on state bucket, BigQuery Admin, Artifact Registry roles, etc.)

2. **Create a Workload Identity Pool + Provider**

   - IAM & Admin → **Workload Identity Federation**  
   - **Add pool** (e.g. `github-pool`) → workload type = “Web identity”
   - After pool is created, **Add provider**:
     - Provider type: OpenID Connect (OIDC)
     - Issuer: `https://token.actions.githubusercontent.com`
     - Attribute mapping (example):

       ```text
       attribute.repository  -> assertion.repository
       attribute.ref         -> assertion.ref
       ```

3. **Allow your GitHub repo to impersonate the SA**

   - Still in IAM → **Service accounts** → your `terraform-ci` SA → **Permissions** → **Grant access**
   - Add principal:
     - **Principal type**: “Workload identity pool” (principal set)
     - Select the pool/provider you created
     - Restrict to your repo with a condition like:

       ```text
       attribute.repository == "DSabarish/mlops-template-v1"
       ```

   - Grant role: **Workload Identity User** (`roles/iam.workloadIdentityUser`)

You’ll now have a provider resource name like:

```text
projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github
```

And an SA email like:

```text
terraform-ci@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

---

### 3. GitHub secrets you need (no key)

In your repo:

- **`WIF_PROVIDER`** = the full provider path, e.g.  
  `projects/123456789012/locations/global/workloadIdentityPools/github-pool/providers/github`
- **`WIF_SERVICE_ACCOUNT`** = the Terraform SA email, e.g.  
  `terraform-ci@dn-project-template.iam.gserviceaccount.com`
- **`TF_STATE_BUCKET`** (optional but recommended) = your GCS bucket for Terraform state

No `GCP_SA_KEY` secret is needed.

---

### 4. What to change in the workflow (conceptually)

Where you currently authenticate with `credentials_json` **or** manual file writing, replace that with:

```yaml
- name: Authenticate to GCP
  uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
    service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
```

After that, `terraform init/plan/apply` will use the short‑lived credentials from WIF (no keys).

---

If you want, next I can **rewrite your current `terraform-infra.yml`** to be 100% WIF‑only (no keys) and show you exactly what to paste.