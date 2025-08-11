"""
Centralized AI service for all model calls in Dwell
Consolidates OpenAI API calls and provides a unified interface
"""

import instructor
from openai import OpenAI
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class AIService:
    """Centralized AI service for all model calls."""

    def __init__(self):
        """Initialize AI service with different client configurations."""
        # Standard OpenAI client
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # OpenAI client with Helicone tracking
        self.helicone_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://oai.hconeai.com/v1",
            default_headers={
                "Helicone-Auth": os.getenv("HELICONE_AUTH"),
            },
        )

        # Instructor-patched client for structured outputs
        self.instructor_client = instructor.patch(
            OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                # Commented out Helicone for instructor calls to avoid conflicts
                # base_url="https://oai.hconeai.com/v1",
                # default_headers={
                #     "Helicone-Auth": os.getenv("HELICONE_AUTH"),
                # }
            )
        )

    def _validate_api_key(self):
        """Validate that OpenAI API key is properly set."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or not api_key.startswith("sk-"):
            raise ValueError("Please enter a valid OpenAI API key!")

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4",
        temperature: float = 0.7,
        use_helicone: bool = True,
    ) -> str:
        """
        Standard chat completion for thread-based conversations.
        Used by: chat pages (What to Do, How to Feel, Perspectives)
        """
        self._validate_api_key()

        client = self.helicone_client if use_helicone else self.openai_client

        completion = client.chat.completions.create(
            temperature=temperature,
            model=model,
            messages=messages,
        )
        return completion.choices[0].message.content

    def simple_completion(
        self,
        system_prompt: str,
        user_input: str,
        model: str = "gpt-4",
        temperature: float = 0.7,
    ) -> str:
        """
        Simple system + user prompt completion.
        Used by: basic AI responses
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ]
        return self.chat_completion(messages, model, temperature, use_helicone=False)

    def structured_completion(
        self, messages: List[Dict[str, str]], response_model: Any, model: str = "gpt-4"
    ) -> Any:
        """
        Structured completion using instructor for typed responses.
        Used by: get_activities_emotions, get_value_comparisons
        """
        self._validate_api_key()

        result = self.instructor_client.chat.completions.create(
            model=model,
            response_model=response_model,
            messages=messages,
        )
        return result

    def extract_activities_emotions(
        self, content: str, user_bio: str, type: str = "journal entry"
    ) -> Any:
        """
        Extract activities and emotions from content.
        Used by: utils.py get_activities_emotions
        """
        from emotions import emotion_descriptions

        system_prompt = f"""Extract the following {type} into a list of salient ActivityEmotions, and how the user feels about that detailed activity and their outcome (please be explicit and complete), if unknown say unknown. Please only use the emotions listed here: {emotion_descriptions}"""
        system_prompt = user_bio + system_prompt

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ]

        from data_model import ActivityEmotions

        result = self.structured_completion(messages, ActivityEmotions)
        return result.act_emotions

    def extract_value_comparisons(
        self, content: str, type: str = "journal entry"
    ) -> Any:
        """
        Extract value comparisons from content.
        Used by: utils.py get_value_comparisons
        """
        from values import value_descriptions

        prompt_suffix = f"""Based on the {type}, make list of value comparisons such as superior A > inferior B (A not equal to B).
Only include if there is sufficient evidence. Only use the values from the list below: 
{value_descriptions}
Please mention the supporting evidence/extract from the material in the ref field.
"""

        messages = [
            {"role": "system", "content": prompt_suffix},
            {"role": "user", "content": content},
        ]

        from data_model import ValuesComparisons

        result = self.structured_completion(messages, ValuesComparisons)
        return result.values

    def chat_thread(self, messages: List[Dict[str, str]], model: str = "gpt-4") -> str:
        """
        Chat thread completion with Helicone tracking.
        Used by: all chat pages for conversations
        """
        return self.chat_completion(messages, model, temperature=0.7, use_helicone=True)

    def retry_on_error(self, max_retries: int = 3):
        """Decorator for retrying failed AI calls."""

        def decorator(func):
            def wrapper(*args, **kwargs):
                for i in range(1, max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        print(f"AI call attempt {i} of {max_retries} failed: {e}")
                        if i == max_retries:
                            raise

            return wrapper

        return decorator


# Global AI service instance
ai_service = AIService()


# Backward compatibility functions
def call_openai2_thread(messages: List[Dict[str, str]], model: str = "gpt-4") -> str:
    """Backward compatibility for chat threads."""
    return ai_service.chat_thread(messages, model)


def generate_response(system_prompt: str, input_text: str, model: str = "gpt-4") -> str:
    """Backward compatibility for simple completions."""
    return ai_service.simple_completion(system_prompt, input_text, model)
