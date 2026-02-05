from llama_cpp import Llama
from llm.llm_interface import LLMInterface

class LocalLLM(LLMInterface):
    def __init__(self, model_path: str):
        self.llm = Llama(
            model_path=model_path,
            n_ctx=4096,
            n_threads=8,
            n_gpu_layers=20  # Metal acceleration
        )

    def generate(self, prompt: str) -> str:
        output = self.llm(
            prompt,
            max_tokens=512,
            temperature=0.2,
            stop=["</json>"]
        )
        return output["choices"][0]["text"].strip()
