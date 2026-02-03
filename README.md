# Rhesis LLM Testing Action

A GitHub Action to run Rhesis test sets against your LLM endpoints in CI/CD pipelines.

## Quick Start

Create `.github/workflows/rhesis-tests.yml` in your repository:

```yaml
name: Rhesis LLM Tests

on:
  workflow_dispatch:
  # Or trigger on push/PR:
  # push:
  #   branches: [main]
  # pull_request:
  #   branches: [main]

env:
  RHESIS_ENDPOINT_NAME: 'Insurance Chatbot'
  RHESIS_TEST_SET_NAME: 'Example Test Set: Insurance Chatbot Quality Evaluation'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Rhesis Tests
        id: rhesis
        uses: rhesis-ai/rhesis-action@v1
        with:
          api-key: ${{ secrets.RHESIS_API_KEY }}
          endpoint-name: ${{ env.RHESIS_ENDPOINT_NAME }}
          test-set-name: ${{ env.RHESIS_TEST_SET_NAME }}
          base-url: 'https://api.rhesis.ai'  # Optional: defaults to Rhesis cloud

      - name: Report Results
        if: always()
        run: |
          echo "## Rhesis Test Results" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "| Metric | Value |" >> $GITHUB_STEP_SUMMARY
          echo "|--------|-------|" >> $GITHUB_STEP_SUMMARY
          echo "| Total | ${{ steps.rhesis.outputs.total }} |" >> $GITHUB_STEP_SUMMARY
          echo "| Passed | ${{ steps.rhesis.outputs.passed }} |" >> $GITHUB_STEP_SUMMARY
          echo "| Failed | ${{ steps.rhesis.outputs.failed }} |" >> $GITHUB_STEP_SUMMARY
          echo "| Success Rate | ${{ steps.rhesis.outputs.success-rate }}% |" >> $GITHUB_STEP_SUMMARY
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `api-key` | Rhesis API key | Yes | - |
| `endpoint-name` | Name of the endpoint to test | Yes | - |
| `test-set-name` | Name of the test set to run | Yes | - |
| `base-url` | Rhesis API base URL (for self-hosted) | No | - |
| `python-version` | Python version to use | No | `3.11` |
| `poll-timeout` | Timeout in seconds for test run to appear | No | `600` |
| `completion-timeout` | Timeout in seconds for test completion | No | `1800` |

## Outputs

| Output | Description |
|--------|-------------|
| `total` | Total number of tests |
| `passed` | Number of passed tests |
| `failed` | Number of failed tests |
| `success-rate` | Test success rate percentage |

## Setup

1. Get your API key from [app.rhesis.ai](https://app.rhesis.ai) → **API Tokens**
2. Add `RHESIS_API_KEY` to your repository secrets (**Settings** → **Secrets and variables** → **Actions**)
3. Copy the workflow example above to `.github/workflows/rhesis-tests.yml`
4. Update `RHESIS_ENDPOINT_NAME` and `RHESIS_TEST_SET_NAME` with your values

## License

MIT
