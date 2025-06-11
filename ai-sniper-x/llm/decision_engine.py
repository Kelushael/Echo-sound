import os
from pathlib import Path

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

try:
    from gpt4all import GPT4All
except ImportError:
    GPT4All = None


class LocalDecisionEngine:
    def __init__(self, model_path: str):
        self.model_path = Path(model_path)
        if Llama and self.model_path.suffix in {'.gguf', '.ggml'}:
            self.llm = Llama(model_path=str(self.model_path), n_ctx=512)
            self.mode = 'llama'
        elif GPT4All and self.model_path.suffix == '.bin':
            self.llm = GPT4All(model_path=str(self.model_path))
            self.mode = 'gpt4all'
        else:
            raise RuntimeError('No supported LLM found for given model path')

    def ask(self, prompt: str) -> str:
        if self.mode == 'llama':
            output = self.llm(prompt, max_tokens=64, stop=['\n'])
            return output['choices'][0]['text'].strip()
        elif self.mode == 'gpt4all':
            return self.llm.generate(prompt, max_tokens=64).strip()
        return ''
