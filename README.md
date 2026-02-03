# Rhesis LLM Testing Action

A GitHub Action to run Rhesis test sets against your LLM endpoints in CI/CD pipelines.

## Quick Start

```yaml
- name: Run Rhesis Tests
  id: rhesis
  uses: rhesis-ai/rhesis-action@v1
  with:
    api-key: ${{ secrets.RHESIS_API_KEY }}
    endpoint-name: my-chatbot
    test-set-name: regression-tests
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
3. Create `.github/workflows/rhesis-tests.yml` with the example above

## License

MIT
