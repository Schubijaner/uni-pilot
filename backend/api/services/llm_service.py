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
        # Use explicit credentials if provided, otherwise use AWS standard credential chain
        # (aws configure, IAM role, environment variables, etc.)
        try:
            client_kwargs = {
                "service_name": "bedrock-runtime",
                "region_name": settings.AWS_REGION,
            }

            # Only add explicit credentials if both are provided
            # Otherwise, boto3 will use the standard credential chain
            if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
                logger.info("Using explicit AWS credentials from config")
                client_kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
                client_kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
            else:
                logger.info(
                    f"Using AWS standard credential chain (aws configure, IAM role, etc.) "
                    f"for region {settings.AWS_REGION}"
                )

            self.bedrock_client = boto3.client(**client_kwargs)

            # Test the client by checking if we can access the service
            # This will raise an exception if credentials are invalid
            logger.info(f"Bedrock client initialized successfully for region {settings.AWS_REGION}")

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_msg = e.response.get("Error", {}).get("Message", str(e))
            logger.error(
                f"Failed to initialize Bedrock client: {error_code} - {error_msg}. "
                f"Please check your AWS credentials and Bedrock model access."
            )
            self.bedrock_client = None
        except Exception as e:
            logger.error(
                f"Failed to initialize Bedrock client: {e}. "
                f"Please ensure AWS credentials are configured via 'aws configure' or environment variables."
            )
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
            raise LLMError(
                "Bedrock client not initialized. "
                "Please configure AWS credentials using 'aws configure' or set AWS_ACCESS_KEY_ID and "
                "AWS_SECRET_ACCESS_KEY environment variables. "
                "Also ensure Bedrock model access is enabled in AWS Console."
            )

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

            # Check if response was truncated (stop_reason indicates why generation stopped)
            stop_reason = response_body.get("stop_reason")
            was_truncated = stop_reason == "max_tokens"
            if was_truncated:
                logger.warning(
                    f"Response was truncated due to max_tokens limit ({max_tokens}). "
                    f"Response may be incomplete."
                )

            # Extract text from response
            text_content = ""
            for block in content:
                if block.get("type") == "text":
                    text_content += block.get("text", "")

            # Store truncation flag in response for later handling
            # We'll attach it as metadata (hack: prefix with special marker)
            if was_truncated:
                text_content = f"__TRUNCATED__{text_content}"

            return text_content

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_msg = e.response.get("Error", {}).get("Message", str(e))
            logger.error(f"Bedrock API error: {error_code} - {error_msg}")

            # Provide helpful error messages for common errors
            if error_code == "AccessDeniedException":
                raise LLMError(
                    f"AWS Bedrock access denied: {error_msg}. "
                    "Please check IAM permissions and ensure Bedrock model access is enabled in AWS Console."
                )
            elif error_code == "ValidationException":
                raise LLMError(f"AWS Bedrock validation error: {error_msg}")
            elif error_code == "ModelNotReadyException":
                raise LLMError(
                    f"Bedrock model not ready: {error_msg}. "
                    "The model may still be initializing. Please try again in a few moments."
                )
            else:
                raise LLMError(f"AWS Bedrock API error ({error_code}): {error_msg}")

        except BotoCoreError as e:
            logger.error(f"Boto3 error: {e}")
            error_msg = str(e)
            if "Unable to locate credentials" in error_msg or "NoCredentialsError" in error_msg:
                raise LLMError(
                    "AWS credentials not found. "
                    "Please configure credentials using 'aws configure' or set AWS_ACCESS_KEY_ID and "
                    "AWS_SECRET_ACCESS_KEY environment variables."
                )
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
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate chat response using Claude Haiku.

        Args:
            system_prompt: System prompt for the conversation
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Sampling temperature (defaults to config)
            max_tokens: Maximum tokens in response (defaults to 2048)

        Returns:
            Assistant response text
        """
        temp = temperature if temperature is not None else settings.CHAT_TEMPERATURE
        max_tok = max_tokens if max_tokens is not None else 2048

        return self._invoke_model(
            model_id=self.model_id_chat,
            messages=messages,
            system_prompt=system_prompt,
            temperature=temp,
            max_tokens=max_tok,
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

        # Use higher max_tokens for roadmap generation (roadmaps can be large)
        # Claude Sonnet supports up to 8192 tokens for output
        response_text = self._invoke_model(
            model_id=self.model_id_roadmap,
            messages=messages,
            system_prompt=None,
            temperature=temp,
            max_tokens=8192,  # Increased from 4096 to handle large roadmaps
        )

        # Parse JSON response
        try:
            # Check if response was marked as truncated
            was_truncated = response_text.startswith("__TRUNCATED__")
            if was_truncated:
                response_text = response_text[13:]  # Remove marker
                logger.warning("Processing truncated response - attempting to salvage partial JSON")

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

            # Try to fix incomplete JSON if truncated
            if was_truncated or (not response_text.endswith("}") and not response_text.endswith("]")):
                logger.warning("Response appears incomplete - attempting to fix JSON structure")
                
                # Find the items array and try to salvage what we can
                items_start = response_text.find('"items": [')
                if items_start > 0:
                    # Find the last complete item in the array
                    items_content = response_text[items_start + 9:]  # After '"items": ['
                    
                    # Find last complete object by counting braces, handling strings properly
                    item_braces = 0
                    last_complete_item = -1
                    in_string = False
                    escape_next = False
                    
                    for i, char in enumerate(items_content):
                        if escape_next:
                            escape_next = False
                            continue
                        if char == '\\':
                            escape_next = True
                            continue
                        if char == '"' and not escape_next:
                            in_string = not in_string
                            continue
                        if not in_string:
                            if char == "{":
                                item_braces += 1
                            elif char == "}":
                                item_braces -= 1
                                if item_braces == 0:
                                    last_complete_item = items_start + 9 + i
                    
                    if last_complete_item > 0:
                        # Close the items array and root object
                        response_text = response_text[:last_complete_item + 1] + "\n  ]\n}"
                        logger.info(f"Fixed truncated JSON by closing items array at position {last_complete_item + 1}")
                    else:
                        # Fallback: try to find any complete item by looking for "}" followed by "," or "]"
                        # This handles cases where we're in the middle of a field
                        last_comma_or_bracket = max(
                            response_text.rfind('},\n'),
                            response_text.rfind('},'),
                            response_text.rfind('}\n')
                        )
                        if last_comma_or_bracket > items_start:
                            # Found a complete item, close from there
                            close_pos = last_comma_or_bracket + 1
                            response_text = response_text[:close_pos] + "\n  ]\n}"
                            logger.info(f"Fixed truncated JSON using fallback at position {close_pos}")
                        else:
                            # Last resort: just close what we have
                            response_text = response_text.rstrip()
                            # Remove trailing comma if present
                            if response_text.endswith(","):
                                response_text = response_text[:-1]
                            # Close items array and root
                            if not response_text.endswith("]"):
                                response_text += "\n  ]"
                            if not response_text.endswith("}"):
                                response_text += "\n}"
                            logger.warning("Applied last-resort JSON repair")

            parsed_response = json.loads(response_text)
            
            if was_truncated:
                logger.warning(
                    f"Successfully parsed truncated response. "
                    f"Roadmap may be incomplete with {len(parsed_response.get('items', []))} items."
                )
            
            return parsed_response

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            # Log more of the response for debugging (first 2000 chars instead of 500)
            response_preview = response_text[:2000] if len(response_text) > 2000 else response_text
            logger.error(f"Response text (first 2000 chars): {response_preview}")
            if len(response_text) > 2000:
                logger.error(f"Response text (last 500 chars): {response_text[-500:]}")
            logger.error(f"Response length: {len(response_text)} characters")
            logger.error(f"Error position: line {e.lineno}, column {e.colno}")
            raise LLMError(f"Failed to parse JSON response from LLM: {e}")

