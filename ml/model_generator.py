#!/usr/bin/env python3
"""
ML Model Generator for Playlist Recommendation System
Uses FP-Growth algorithm to generate association rules from playlist data
"""

import os
import sys
import pickle
from datetime import datetime
import pandas as pd
from fpgrowth_py import fpgrowth

# Configuration from environment variables or defaults
DATASET_PATH = os.environ.get('DATASET_PATH', '../2023_spotify_ds1.csv')
MODEL_OUTPUT_PATH = os.environ.get('MODEL_OUTPUT_PATH', '../models/recommendation_model.pkl')
MIN_SUPPORT = float(os.environ.get('MIN_SUPPORT', '0.05'))  # 5% minimum support (higher = less memory)
MIN_CONFIDENCE = float(os.environ.get('MIN_CONFIDENCE', '0.5'))  # 50% minimum confidence
SAMPLE_SIZE = int(os.environ.get('SAMPLE_SIZE', '10000'))  # Sample 10k playlists for local testing

def load_and_process_dataset(dataset_path):
    """
    Load Spotify playlist dataset and convert to transaction format
    Each transaction is a list of song names from one playlist
    """
    print(f"Loading dataset from: {dataset_path}")

    if not os.path.exists(dataset_path):
        print(f"Error: Dataset not found at {dataset_path}")
        sys.exit(1)

    # Read CSV
    df = pd.read_csv(dataset_path)
    print(f"Loaded {len(df)} tracks from dataset")

    # Group by playlist ID (pid) to create transactions
    print("Grouping tracks by playlist...")
    playlists = df.groupby('pid')['track_name'].apply(list).tolist()
    print(f"Created {len(playlists)} playlists (transactions)")

    # Sample playlists if SAMPLE_SIZE is set and positive
    if SAMPLE_SIZE > 0 and len(playlists) > SAMPLE_SIZE:
        print(f"Sampling {SAMPLE_SIZE} playlists for efficiency...")
        import random
        random.seed(42)  # For reproducibility
        playlists = random.sample(playlists, SAMPLE_SIZE)
        print(f"Using {len(playlists)} sampled playlists")

    # Filter out empty playlists
    playlists = [p for p in playlists if len(p) > 0]
    print(f"After filtering: {len(playlists)} non-empty playlists")

    return playlists, df

def generate_association_rules(playlists, min_support, min_confidence):
    """
    Use FP-Growth algorithm to generate frequent itemsets and association rules
    """
    print(f"\nGenerating association rules with:")
    print(f"  - Minimum Support: {min_support}")
    print(f"  - Minimum Confidence: {min_confidence}")

    try:
        freq_itemsets, rules = fpgrowth(
            playlists,
            minSupRatio=min_support,
            minConf=min_confidence
        )

        print(f"\nResults:")
        print(f"  - Frequent itemsets found: {len(freq_itemsets)}")
        print(f"  - Association rules generated: {len(rules)}")

        return freq_itemsets, rules

    except Exception as e:
        print(f"Error during FP-Growth: {e}")
        sys.exit(1)

def save_model(model_data, output_path):
    """
    Save the model (rules + metadata) using pickle
    """
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    print(f"\nSaving model to: {output_path}")

    with open(output_path, 'wb') as f:
        pickle.dump(model_data, f)

    print(f"Model saved successfully!")
    print(f"File size: {os.path.getsize(output_path) / 1024:.2f} KB")

def main():
    """
    Main function to orchestrate model generation
    """
    print("="*60)
    print("Playlist Recommendation Model Generator")
    print("="*60)
    print()

    # Load and process dataset
    playlists, raw_df = load_and_process_dataset(DATASET_PATH)

    # Generate association rules
    freq_itemsets, rules = generate_association_rules(playlists, MIN_SUPPORT, MIN_CONFIDENCE)

    # Prepare model data with metadata
    model_data = {
        'rules': rules,
        'freq_itemsets': freq_itemsets,
        'metadata': {
            'model_date': datetime.now().isoformat(),
            'dataset_path': DATASET_PATH,
            'num_playlists': len(playlists),
            'num_tracks': len(raw_df),
            'min_support': MIN_SUPPORT,
            'min_confidence': MIN_CONFIDENCE,
            'num_rules': len(rules),
            'version': '1.0'
        }
    }

    # Save model
    save_model(model_data, MODEL_OUTPUT_PATH)

    print("\n" + "="*60)
    print("Model generation completed successfully!")
    print("="*60)
    print("\nModel Metadata:")
    for key, value in model_data['metadata'].items():
        print(f"  {key}: {value}")

    # Show sample rules
    if rules and len(rules) > 0:
        print("\nSample Association Rules (first 5):")
        for i, rule in enumerate(rules[:5], 1):
            antecedent = rule[0]  # if
            consequent = rule[1]  # then
            confidence = rule[2]
            print(f"  {i}. IF {antecedent} THEN {consequent} (confidence: {confidence:.2%})")

    return 0

if __name__ == "__main__":
    sys.exit(main())
