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
        """Generate with JSON schema constraint"""
        formatted_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You output only valid JSON.<|eot_id|><|start_header_id|>user<|end_header_id|>
{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
        output = self.llm.create_chat_completion(
            messages=[
                {"role": "system", "content": "You output only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},  # Force JSON
            temperature=0.1,
            max_tokens=512
        )
        return output["choices"][0]["message"]["content"]
