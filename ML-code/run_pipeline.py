"""
Run full pipeline: generate_data -> bq_ingestion -> gcs_ingestion -> clean -> transform -> train (save to GCS).
"""
from generate_data import generate_data
from bq_ingestion import save_to_bq
from gcs_ingestion import bq_to_gcs
from clean import clean
from transformation import transform
from train import train_and_save_to_gcs


def run():

    print("1. Generate data (100 records, 5 cols, 1 target)")
    df = generate_data(100)
    
    print("2. Save to BQ")
    save_to_bq(df)
    
    print("3. BQ -> GCS (versioned)")
    uri = bq_to_gcs()
    print("   ", uri)
    
    print("4. Clean")
    df = clean(df)
    
    print("5. Transform")
    X, y = transform(df)
    
    print("6. Train and save to GCS only (latest + versioned)")
    _, latest, versioned, metrics = train_and_save_to_gcs(X, y)
    
    print("   Latest:", latest)
    print("   Versioned:", versioned)
    print("   Metrics:", metrics)
    return latest


if __name__ == "__main__":
    run()
