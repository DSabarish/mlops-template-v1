project_id  = "my-prod-project"
region      = "asia-south1"
environment = "prod"
prefix      = "mlapp"

labels = {
  owner       = "ml-team"
  environment = "prod"
}

dataset_id       = "training_dataset"
table_id         = "features_table"
dataset_location = "asia-south1"

dataset_delete_on_destroy = false
bucket_force_destroy      = false

artifacts_retention_days = 90
data_retention_days      = 30

table_schema = [
  { name = "f1", type = "FLOAT", mode = "NULLABLE" },
  { name = "f2", type = "FLOAT", mode = "NULLABLE" },
  { name = "f3", type = "FLOAT", mode = "NULLABLE" },
  { name = "f4", type = "FLOAT", mode = "NULLABLE" },
  { name = "f5", type = "FLOAT", mode = "NULLABLE" },
  { name = "T", type = "FLOAT", mode = "NULLABLE" }
]