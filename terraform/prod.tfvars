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
  { name = "feature_1", type = "FLOAT", mode = "NULLABLE" },
  { name = "feature_2", type = "FLOAT", mode = "NULLABLE" },
  { name = "feature_3", type = "FLOAT", mode = "NULLABLE" },
  { name = "feature_4", type = "FLOAT", mode = "NULLABLE" },
  { name = "feature_5", type = "FLOAT", mode = "NULLABLE" }
]