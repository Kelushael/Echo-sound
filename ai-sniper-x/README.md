# AI Sniper X

An experimental crypto trading bot with locally hosted LLM decision engine. This project demonstrates a high-speed Solana sniper that can execute trades autonomously and bridge profits to BTC. All AI logic runs via local models using `llama-cpp-python` or `gpt4all`.

## Structure

- `main.py` – orchestrates wallet loading, funding checks, trading loop, and bridging.
- `config/` – configuration files including `.env.example` and runtime settings.
- `llm/` – local LLM integration used for dynamic trade decisions.
- `wallet/` – wallet loader and funding utilities.
- `trading/` – sniper logic and transaction execution.
- `bridge/` – optional SOL→BTC bridge module.
- `utils/` – logging and scheduling helpers.

## Running

1. Copy `config/.env.example` to `.env` and fill in your Solana RPC endpoint and optional parameters.
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Execute the bot:
   ```sh
   python main.py
   ```

### GitHub Actions

You can also run the bot via GitHub Actions. Create a repository secret
`ANT_API_KEY` with your API token and trigger the **Run AI Sniper X** workflow.

LLM models must be downloaded locally. This script will attempt to use `llama-cpp-python` first and fall back to `gpt4all` if available.
