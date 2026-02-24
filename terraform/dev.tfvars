# terraform\dev.tfvars
#v1

# -------------------------------------------------------
project_id  = "dn-project-template" 
region      = "asia-south1"
environment = "dev"
prefix      = "sabs"

labels = {
  owner       = "dn-team"
  environment = "dev"
}


# -------------------------------------------------------
dataset_id       = "training_dataset_dev"
table_id         = "features_table"
dataset_location = "asia-south1"

dataset_delete_on_destroy = true
bucket_force_destroy      = true

artifacts_retention_days = 7
data_retention_days      = 3

# -------------------------------------------------------
# f1..f5 = features, T = target (per MLOps schema)
table_schema = [
  { name = "f1", type = "FLOAT", mode = "NULLABLE" },
  { name = "f2", type = "FLOAT", mode = "NULLABLE" },
  { name = "f3", type = "FLOAT", mode = "NULLABLE" },
  { name = "f4", type = "FLOAT", mode = "NULLABLE" },
  { name = "f5", type = "FLOAT", mode = "NULLABLE" },
  { name = "T", type = "FLOAT", mode = "NULLABLE" }
]