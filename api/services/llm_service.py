"""LLM Service for AWS Bedrock integration."""

import json
import logging
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from api.core.config import get_settings
from api.core.exceptions import LLMError

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMService:
    """Service for interacting with AWS Bedrock LLM models."""

    def __init__(
        self,
        model_id_chat: Optional[str] = None,
        model_id_roadmap: Optional[str] = None,
    ):
        """
        Initialize LLM Service with AWS Bedrock client.

        Args:
            model_id_chat: Bedrock model ID for chat (defaults to config)
            model_id_roadmap: Bedrock model ID for roadmap generation (defaults to config)
        """
        self.model_id_chat = model_id_chat or settings.BEDROCK_MODEL_CHAT
        self.model_id_roadmap = model_id_roadmap or settings.BEDROCK_MODEL_ROADMAP

        # Initialize Bedrock client
        try:
            self.bedrock_client = boto3.client(
                service_name="bedrock-runtime",
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            # For development, we might not have AWS credentials yet
            self.bedrock_client = None

    def _invoke_model(
        self,
        model_id: str,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """
        Invoke AWS Bedrock model.

        Args:
            model_id: Bedrock model ID
            messages: List of messages (format: [{"role": "user", "content": "..."}])
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            Response text from model

        Raises:
            LLMError: If API call fails
        """
        if not self.bedrock_client:
            raise LLMError("Bedrock client not initialized. Check AWS credentials.")

        try:
            # Format messages for Claude API
            # Claude uses "user" and "assistant" roles
            formatted_messages = []
            for msg in messages:
                formatted_messages.append(
                    {
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", ""),
                    }
                )

            # Prepare request body
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": formatted_messages,
            }

            if system_prompt:
                body["system"] = system_prompt

            # Invoke model
            response = self.bedrock_client.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json",
            )

            # Parse response
            response_body = json.loads(response["body"].read())
            content = response_body.get("content", [])

            if not content:
                raise LLMError("Empty response from Bedrock API")

            # Extract text from response
            text_content = ""
            for block in content:
                if block.get("type") == "text":
                    text_content += block.get("text", "")

            return text_content

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_msg = e.response.get("Error", {}).get("Message", str(e))
            logger.error(f"Bedrock API error: {error_code} - {error_msg}")
            raise LLMError(f"AWS Bedrock API error: {error_code} - {error_msg}")

        except BotoCoreError as e:
            logger.error(f"Boto3 error: {e}")
            raise LLMError(f"Boto3 error: {e}")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Bedrock response: {e}")
            raise LLMError("Failed to parse response from Bedrock API")

        except Exception as e:
            logger.error(f"Unexpected error in LLM service: {e}")
            raise LLMError(f"Unexpected error: {e}")

    def chat(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate chat response using Claude Haiku.

        Args:
            system_prompt: System prompt for the conversation
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Sampling temperature (defaults to config)

        Returns:
            Assistant response text
        """
        temp = temperature if temperature is not None else settings.CHAT_TEMPERATURE

        return self._invoke_model(
            model_id=self.model_id_chat,
            messages=messages,
            system_prompt=system_prompt,
            temperature=temp,
            max_tokens=2048,
        )

    def generate_roadmap(
        self,
        prompt: str,
        response_schema: Optional[Dict[str, Any]] = None,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Generate roadmap using Claude Sonnet with structured output.

        Args:
            prompt: Prompt for roadmap generation
            response_schema: Optional JSON schema for structured output
            temperature: Sampling temperature (defaults to config)

        Returns:
            Parsed JSON response as dictionary
        """
        temp = temperature if temperature is not None else settings.ROADMAP_TEMPERATURE

        messages = [{"role": "user", "content": prompt}]

        response_text = self._invoke_model(
            model_id=self.model_id_roadmap,
            messages=messages,
            system_prompt=None,
            temperature=temp,
            max_tokens=4096,
        )

        # Parse JSON response
        try:
            # Try to extract JSON from response (sometimes LLM adds markdown)
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                # Remove markdown code block
                response_text = response_text[7:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
            elif response_text.startswith("```"):
                # Remove generic code block
                response_text = response_text[3:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()

            parsed_response = json.loads(response_text)
            return parsed_response

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response_text[:500]}")
            raise LLMError(f"Failed to parse JSON response from LLM: {e}")

