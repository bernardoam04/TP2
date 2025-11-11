#!/usr/bin/env python3
"""
CLI Client for Playlist Recommendation API
Sends song names to the API and displays recommendations
"""

import sys
import argparse
import json
import requests
from typing import List

# Default API configuration
DEFAULT_API_URL = "http://127.0.0.1:5000/api/recommend"
DEFAULT_TIMEOUT = 10  # seconds

def get_recommendations(songs: List[str], api_url: str = DEFAULT_API_URL, timeout: int = DEFAULT_TIMEOUT):
    """
    Send a recommendation request to the API

    Args:
        songs: List of song names
        api_url: URL of the recommendation API endpoint
        timeout: Request timeout in seconds

    Returns:
        Response JSON dict or None on error
    """
    # Prepare request payload
    payload = {
        "songs": songs
    }

    # Send POST request
    try:
        print(f"Sending request to: {api_url}")
        print(f"Input songs: {songs}")
        print()

        response = requests.post(
            api_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=timeout
        )

        # Check response status
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: API returned status code {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error message: {error_data.get('message', 'Unknown error')}")
            except:
                print(f"Response: {response.text}")
            return None

    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to API at {api_url}")
        print("Make sure the Flask server is running!")
        return None
    except requests.exceptions.Timeout:
        print(f"Error: Request timed out after {timeout} seconds")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def display_recommendations(response_data):
    """
    Display the recommendation response in a user-friendly format
    """
    print("="*60)
    print("RECOMMENDATION RESULTS")
    print("="*60)
    print()

    # Display metadata
    print(f"Server Version: {response_data.get('version', 'N/A')}")
    print(f"Model Date: {response_data.get('model_date', 'N/A')}")
    print(f"Number of Recommendations: {response_data.get('num_recommendations', 0)}")
    print()

    # Display recommendations
    recommendations = response_data.get('songs', [])
    if recommendations:
        print("Recommended Songs:")
        print("-"*60)
        for i, song in enumerate(recommendations, 1):
            print(f"{i:2d}. {song}")
    else:
        print("No recommendations found for the given songs.")
        print("Try different songs or check if the model has sufficient data.")

    print()
    print("="*60)

def check_health(api_base_url: str):
    """
    Check the health of the API server
    """
    health_url = api_base_url.replace('/api/recommend', '/health')

    try:
        response = requests.get(health_url, timeout=5)
        health_data = response.json()

        print("API Health Check:")
        print(f"  Status: {health_data.get('status', 'unknown')}")
        print(f"  Model Loaded: {health_data.get('model_loaded', False)}")
        print(f"  Version: {health_data.get('version', 'N/A')}")
        print()

        return health_data.get('status') == 'healthy'

    except Exception as e:
        print(f"Could not check API health: {e}")
        return False

def main():
    """
    Main function - parse arguments and make API request
    """
    parser = argparse.ArgumentParser(
        description='Get playlist recommendations from the API',
        epilog='Example: python client.py "Yesterday" "Bohemian Rhapsody" "Hotel California"'
    )

    parser.add_argument(
        'songs',
        nargs='+',
        help='Song names to base recommendations on (one or more)'
    )

    parser.add_argument(
        '--url',
        default=DEFAULT_API_URL,
        help=f'API endpoint URL (default: {DEFAULT_API_URL})'
    )

    parser.add_argument(
        '--timeout',
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f'Request timeout in seconds (default: {DEFAULT_TIMEOUT})'
    )

    parser.add_argument(
        '--health',
        action='store_true',
        help='Check API health before making request'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='Output response as raw JSON'
    )

    args = parser.parse_args()

    # Health check if requested
    if args.health:
        if not check_health(args.url):
            print("Warning: API may not be healthy, but continuing anyway...")
            print()

    # Get recommendations
    response_data = get_recommendations(args.songs, args.url, args.timeout)

    if response_data:
        if args.json:
            # Output raw JSON
            print(json.dumps(response_data, indent=2))
        else:
            # Display formatted results
            display_recommendations(response_data)
        return 0
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())
