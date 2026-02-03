#!/usr/bin/env python3
"""
Rhesis CI/CD Test Runner
Executes test sets and validates results for CI/CD pipelines.
"""

import json
import os
import sys
import time
from datetime import datetime

from rhesis.sdk.entities import Endpoints, TestRun, TestRuns, TestSets


def set_github_output(name, value):
    """Set GitHub Actions output variable."""
    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"{name}={value}\n")


def poll_for_test_run(test_configuration_id, timeout=600):
    """Poll for test run to appear after execution."""
    print(f"⏳ Polling for test run (timeout: {timeout}s)...")
    start_time = time.time()
    poll_count = 0

    while time.time() - start_time < timeout:
        poll_count += 1
        test_runs = TestRuns.all(filter=f"test_configuration_id eq '{test_configuration_id}'")

        if test_runs:
            print(f"✓ Test run found: {test_runs[0].id}")
            return test_runs[0].id

        print(f"  Poll {poll_count}: Waiting for test run...")
        time.sleep(10)

    raise TimeoutError(f"No test run appeared after {timeout} seconds")


def wait_for_completion(test_run, timeout=1800):
    """Wait for test run to complete."""
    print(f"⏳ Waiting for test run completion (timeout: {timeout}s)...")
    start_time = time.time()
    poll_count = 0

    while time.time() - start_time < timeout:
        poll_count += 1
        test_run.pull()
        status = test_run.status.value if test_run.status else ""

        print(f"  Poll {poll_count}: Status = {status}")

        if status in ["Completed", "Partial", "Failed"]:
            print(f"✓ Test run completed with status: {status}")
            return

        time.sleep(30)

    raise TimeoutError(f"Test run did not complete after {timeout} seconds")


def get_test_results(test_run_id):
    """Retrieve and analyze test results."""
    print("📊 Retrieving test results...")
    test_run = TestRun(id=test_run_id)
    test_results = test_run.get_test_results()

    total = len(test_results)
    failed_tests = []
    passed_tests = []

    for result in test_results:
        status = result["status"]["name"]
        test_id = (
            result.get("test_id", result.get("id", "unknown"))
            if isinstance(result, dict)
            else result.test_id
        )

        is_failed = any(fail_word in str(status).lower() for fail_word in ["fail", "error"])

        if is_failed:
            failed_tests.append({"test_id": test_id, "status": status})
        else:
            passed_tests.append(test_id)

    passed = len(passed_tests)
    failed = len(failed_tests)
    success_rate = (passed / total * 100) if total > 0 else 0.0

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "success_rate": success_rate,
        "failed_tests": failed_tests,
    }


def print_summary(summary):
    """Print test results summary."""
    print("\n" + "=" * 60)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Total tests:    {summary['total']}")
    print(f"Passed:         {summary['passed']} ✓")
    print(f"Failed:         {summary['failed']} ✗")
    print(f"Success rate:   {summary['success_rate']:.1f}%")
    print("=" * 60)

    if summary["failed_tests"]:
        print("\n❌ FAILED TESTS:")
        for ft in summary["failed_tests"][:10]:
            print(f"  • Test ID: {ft['test_id']} (Status: {ft['status']})")

        if len(summary["failed_tests"]) > 10:
            print(f"  ... and {len(summary['failed_tests']) - 10} more")
    print()


def save_results(summary, filename="test-results.json"):
    """Save test results to file for artifacts."""
    results = {"timestamp": datetime.utcnow().isoformat(), "summary": summary}

    with open(filename, "w") as f:
        json.dump(results, f, indent=2)

    print(f"💾 Results saved to {filename}")


def main():
    """Main CI/CD test execution workflow."""
    print("\n🚀 Starting Rhesis CI/CD Test Execution")
    print("=" * 60)

    # Get configuration from environment
    endpoint_name = os.getenv("RHESIS_ENDPOINT_NAME")
    test_set_name = os.getenv("RHESIS_TEST_SET_NAME")
    poll_timeout = int(os.getenv("RHESIS_POLL_TIMEOUT", "600"))
    completion_timeout = int(os.getenv("RHESIS_COMPLETION_TIMEOUT", "1800"))
    success_threshold = float(os.getenv("RHESIS_SUCCESS_THRESHOLD", "100"))

    if not endpoint_name or not test_set_name:
        print("❌ Error: RHESIS_ENDPOINT_NAME and RHESIS_TEST_SET_NAME must be set")
        sys.exit(1)

    try:
        # Step 1: Get endpoint
        print(f"\n📍 Step 1: Retrieving endpoint '{endpoint_name}'")
        endpoint = Endpoints.pull(name=endpoint_name)
        print(f"✓ Endpoint retrieved: {endpoint.name}")

        # Step 2: Get test set
        print(f"\n📦 Step 2: Retrieving test set '{test_set_name}'")
        test_set = TestSets.pull(name=test_set_name)
        print(f"✓ Test set retrieved: {test_set.name}")

        # Step 3: Execute test set
        print("\n▶️  Step 3: Executing test set against endpoint")
        execution_response = test_set.execute(endpoint=endpoint)
        test_configuration_id = execution_response.get("test_configuration_id")

        print(f"✓ Test execution initiated (config: {test_configuration_id})")

        # Step 4: Poll for test run
        print("\n🔍 Step 4: Polling for test run")
        test_run_id = poll_for_test_run(test_configuration_id, timeout=poll_timeout)

        # Step 5: Wait for completion
        print("\n⏰ Step 5: Monitoring test run completion")
        test_run = TestRun(id=test_run_id)
        wait_for_completion(test_run, timeout=completion_timeout)

        # Step 6: Get results
        print("\n📊 Step 6: Retrieving test results")
        summary = get_test_results(test_run_id)

        # Print and save results
        print_summary(summary)
        save_results(summary)

        # Set GitHub Actions outputs
        set_github_output("total", summary["total"])
        set_github_output("passed", summary["passed"])
        set_github_output("failed", summary["failed"])
        set_github_output("success_rate", f"{summary['success_rate']:.1f}")

        # Step 7: Check against threshold
        if summary["success_rate"] < success_threshold:
            print("\n❌ CI/CD PIPELINE FAILED")
            print(f"   {summary['failed']}/{summary['total']} tests failed")
            print(f"   Success rate: {summary['success_rate']:.1f}% (Required: {success_threshold:.1f}%)")
            sys.exit(1)

        print("\n✅ CI/CD PIPELINE PASSED")
        print(f"   Success rate: {summary['success_rate']:.1f}% (Threshold: {success_threshold:.1f}%)")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
