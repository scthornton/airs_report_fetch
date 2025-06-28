#!/usr/bin/env python3
"""
Palo Alto Networks AI Runtime Security Report Retrieval Script

Recommended to set your environment variables and not hardcode them. 

"""

import os
import requests
import json
from datetime import datetime

# --- Configuration ---
API_KEY = os.getenv("PANW_AI_SEC_API_KEY",
                    "YOUR_API_KEY")
PROFILE_NAME = os.getenv("PANW_AI_SEC_PROFILE", "YOUR_SECURITY_PROFILE_NAME")
API_ENDPOINT_BASE = os.getenv(
    "PANW_AI_SEC_ENDPOINT", "https://service.api.aisecurity.paloaltonetworks.com")

# Working API endpoints
SCAN_SYNC_PATH = "/v1/scan/sync/request"
REPORTS_PATH = "/v1/scan/reports"
FULL_SCAN_URL = f"{API_ENDPOINT_BASE}{SCAN_SYNC_PATH}"
FULL_REPORTS_URL = f"{API_ENDPOINT_BASE}{REPORTS_PATH}"


def test_scan_endpoint():
    """Test the scan endpoint with proper payload"""
    print("🔍 Testing scan endpoint with proper payload...")

    headers = {
        "x-pan-token": API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "tr_id": f"test-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "ai_profile": {"profile_name": PROFILE_NAME},
        "metadata": {
            "app_user": "test_user",
            "ai_model": "Test Model",
            "app_name": "Report Test Script"
        },
        "contents": [{"prompt": "Hello, this is a test prompt for reporting"}]
    }

    print(f"URL: {FULL_SCAN_URL}")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(
            FULL_SCAN_URL, headers=headers, json=payload, timeout=30)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Scan successful!")
            print(f"Response: {json.dumps(result, indent=2)}")

            # Extract report_id for testing reports endpoint
            report_id = result.get("report_id")
            if report_id:
                print(f"\n📋 Got report_id: {report_id}")
                return report_id
            else:
                print("⚠️ No report_id in response")

        else:
            print(f"❌ Scan failed: {response.text}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

    return None


def test_reports_endpoint(report_id):
    """Test the reports endpoint with a valid report_id"""
    print(f"\n🔍 Testing reports endpoint with report_id: {report_id}")

    headers = {
        "x-pan-token": API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Try different formats for the report_ids parameter
    formats_to_try = [
        f"?report_ids={report_id}",
        f"?report_ids=[{report_id}]",
        f"?report_ids=[\"{report_id}\"]"
    ]

    for fmt in formats_to_try:
        url = f"{FULL_REPORTS_URL}{fmt}"
        print(f"\nTrying: {url}")

        try:
            response = requests.get(url, headers=headers, timeout=30)
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                print("✅ Reports endpoint working!")
                result = response.json()
                print(f"Report data: {json.dumps(result, indent=2)}")
                return result
            else:
                print(f"Response: {response.text[:200]}...")

        except Exception as e:
            print(f"❌ Error: {str(e)}")

    return None


def get_report_by_id(report_id):
    """Get a specific report using the working format"""
    headers = {
        "x-pan-token": API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Use the format that works
    url = f"{FULL_REPORTS_URL}?report_ids={report_id}"

    print(f"Fetching report: {report_id}")
    print(f"URL: {url}")

    try:
        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code}: {response.text[:200]}")
            return None

    except Exception as e:
        print(f"Error: {str(e)}")
        return None


def generate_test_scan(prompt_text):
    """Generate a test scan and return the report_id"""
    headers = {
        "x-pan-token": API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "tr_id": f"test-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "ai_profile": {"profile_name": PROFILE_NAME},
        "metadata": {
            "app_user": "report_test_user",
            "ai_model": "Test Model",
            "app_name": "Report Test Script"
        },
        "contents": [{"prompt": prompt_text}]
    }

    try:
        response = requests.post(
            FULL_SCAN_URL, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            return result.get("report_id")
        else:
            print(
                f"Scan failed: {response.status_code} - {response.text[:200]}")
            return None

    except Exception as e:
        print(f"Error generating scan: {str(e)}")
        return None


def main():
    """Main function with updated options"""
    print("=" * 60)
    print("🛡️  Palo Alto Networks AI Security Report Retriever - WORKING")
    print("=" * 60)

    while True:
        print("\nChoose an option:")
        print("1. Test scan endpoint (generate test scan)")
        print("2. Test both scan + reports (full workflow)")
        print("3. Get specific report by ID")
        print("4. Exit")

        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":
            print("\n📊 Testing scan endpoint...")
            report_id = test_scan_endpoint()
            if report_id:
                print(f"✅ Success! Generated report_id: {report_id}")
            else:
                print("❌ Failed to generate scan")

        elif choice == "2":
            print("\n🔄 Testing full workflow (scan + reports)...")

            # Step 1: Generate test scan
            print("Step 1: Generating test scan...")
            report_id = test_scan_endpoint()

            if report_id:
                # Step 2: Test reports endpoint
                print("\nStep 2: Testing reports endpoint...")
                report_data = test_reports_endpoint(report_id)

                if report_data:
                    print("\n✅ Full workflow successful!")
                    print(
                        "You can now use this script to get reports with real report IDs")
                else:
                    print("\n❌ Reports endpoint test failed")
            else:
                print("\n❌ Cannot test reports without valid report_id")

        elif choice == "3":
            report_ids_input = input(
                "\nEnter report ID(s) (comma-separated): ").strip()
            if report_ids_input:
                report_ids = [rid.strip()
                              for rid in report_ids_input.split(",") if rid.strip()]

                print(f"\n📋 Fetching {len(report_ids)} report(s)...")

                for report_id in report_ids:
                    print(f"\n--- Report: {report_id} ---")
                    report_data = get_report_by_id(report_id)

                    if report_data:
                        print("✅ Success!")
                        print(json.dumps(report_data, indent=2))
                    else:
                        print("❌ Failed to retrieve report")
            else:
                print("No report IDs provided.")

        elif choice == "4":
            print("Goodbye! 👋")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
