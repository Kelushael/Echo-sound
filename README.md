# Echo-sound

This repository contains experiments with automated cryptocurrency trading bots. The latest module, **AI Sniper X**, demonstrates a proof-of-concept Solana sniper that uses locally hosted LLMs for autonomous trading decisions.

See [`ai-sniper-x/README.md`](ai-sniper-x/README.md) for details.

## GitHub Actions

The repository includes a workflow that can run the sniper bot on a schedule.
To enable it, add a repository secret named `ANT_API_KEY` containing your API
token (for example the string starting with `sk-ant-api03`). The workflow file is
located at `.github/workflows/gpt-action.yml`.
