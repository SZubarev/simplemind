from typing import Union

import groq
import instructor

from simplemind.models import Conversation, Message
from simplemind.providers._base import BaseProvider
from simplemind.settings import settings

PROVIDER_NAME = "groq"
DEFAULT_MODEL = "llama3-8b-8192"


class Groq(BaseProvider):
    __name__ = PROVIDER_NAME
    DEFAULT_MODEL = DEFAULT_MODEL

    def __init__(self, api_key: Union[str, None] = None):
        self.api_key = api_key or settings.get_api_key(PROVIDER_NAME)

    @property
    def client(self):
        """The raw Groq client."""
        if not self.api_key:
            raise ValueError("Groq API key is required")
        return groq.Groq(api_key=self.api_key)

    @property
    def structured_client(self):
        """A client patched with Instructor."""
        return instructor.from_groq(self.client)

    def send_conversation(self, conversation: Conversation) -> Message:
        """Send a conversation to the Groq API."""
        messages = [
            {"role": msg.role, "content": msg.text} for msg in conversation.messages
        ]

        response = self.client.chat.completions.create(
            model=conversation.llm_model or DEFAULT_MODEL, messages=messages
        )

        # Get the response content from the Groq response
        assistant_message = response.choices[0].message

        # Create and return a properly formatted Message instance
        return Message(
            role="assistant",
            text=assistant_message.content or "",
            raw=response,
            llm_model=conversation.llm_model or DEFAULT_MODEL,
            llm_provider=PROVIDER_NAME,
        )

    def structured_response(self, prompt: str, response_model):
        # Ensure messages are provided in kwargs
        messages = [
            {"role": "user", "content": prompt},
        ]

        response = self.structured_client.chat.completions.create(
            messages=messages,
            response_model=response_model,
        )
        return response

    def generate_text(self, prompt: str, *, llm_model: str):
        messages = [
            {"role": "user", "content": prompt},
        ]

        response = self.structured_client.chat.completions.create(
            messages=messages, model=llm_model
        )

        return response.choices[0].message.content
