import litellm
import asyncio
from typing import List, Dict, Any
import logging
logger = logging.getLogger(__name__)

class LiteLLMManager:
    def __init__(self):
        litellm.set_verbose=True
        self.retry_delay = 1
        self.token_usage = {}
        self.model = 'mistral/mistral-medium'
        self.embed_model = 'mistral/mistral-embed'


    async def completion_with_retries(self, messages: List[Dict[str, str]], max_tokens: int, max_retries: int = 5):
        for attempt in range(max_retries):
            try:
                response = await litellm.acompletion(self.model, messages=messages, max_tokens=max_tokens)
                self._update_token_usage(response.usage)
                return response
            except litellm.RateLimitError as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    self.retry_delay *= 2
                else:
                    raise e
            except Exception as e:
                print(f"Unexpected error: {e}")
                raise e

    def _update_token_usage(self,  usage):
        if self.model not in self.token_usage:
            self.token_usage[self.model] = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        self.token_usage[self.model]["prompt_tokens"] += usage.prompt_tokens
        self.token_usage[self.model]["completion_tokens"] += usage.completion_tokens
        self.token_usage[self.model]["total_tokens"] += usage.total_tokens

    
    async def get_embedding(self, text: str) -> List[float]:
        try:
            logger.info(f"Generating embedding for text: {text[:100]}...")  # Log first 100 characters of the text
            response = litellm.embedding(
                model=self.embed_model,
                input=[text]
            )
            logger.info(f"Embedding response: {response}")
            if 'data' in response and response['data'] and 'embedding' in response['data'][0]:
                embedding_result = response['data'][0]['embedding']
                logger.info(f"Embedding generated successfully. Length: {len(embedding_result)}")
                return embedding_result
            else:
                logger.error(f"Unexpected embedding response structure: {response}")
                raise ValueError("Unexpected embedding response structure")
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            logger.error(f"Text: {text}")
            raise
    
    

    def get_token_usage(self):
        return self.token_usage