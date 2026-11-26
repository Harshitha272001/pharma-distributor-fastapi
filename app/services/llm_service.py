import json

import httpx
from pydantic import BaseModel, ValidationError

from app.core.config import settings
from app.schemas.batch import BatchInput


# Address of the LLM chat API
LLM_API_URL = "https://api.openai.com/v1/chat/completions"


# Raised when no LLM key is set
class LLMNotConfiguredError(Exception):
    pass


# Raised when the LLM API call itself fails
class LLMRequestError(Exception):
    pass


# Raised when the LLM output is still unusable after a retry
class LLMParseError(Exception):
    pass


# Shape of the invoice data the LLM must return
class ParsedInvoice(BaseModel):
    invoice_number: str
    distributor_name: str
    invoice_date: str
    total_amount: float
    batches: list[BatchInput] = []


# Instructions sent to the LLM with every request
SYSTEM_PROMPT = (
    "You read pharma supplier invoices. Extract the invoice number, "
    "distributor name, invoice date, total amount, and every batch "
    "(batch number, medicine name, quantity, manufacturing date, "
    "expiry date). Reply with JSON only, no other text. "
    "Dates as YYYY-MM-DD. Use this shape: "
    '{"invoice_number": "...", "distributor_name": "...", '
    '"invoice_date": "2026-01-10", "total_amount": 45000, '
    '"batches": [{"batch_number": "...", "medicine_name": "...", '
    '"quantity": 1000, "manufacturing_date": "2026-01-10", '
    '"expiry_date": "2027-12-31"}]}'
)


# Ask the LLM to read invoice text and return invoice data as JSON
def parse_invoice_text(text: str) -> ParsedInvoice:

    # No key means the LLM endpoint cannot run
    if not settings.LLM_API_KEY:
        raise LLMNotConfiguredError(
            "LLM_API_KEY is not set. Add it to your .env file."
        )

    # First attempt, then one retry if the output fails validation
    last_error = None

    for attempt in range(2):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ]

        # On retry, show the LLM what was wrong last time
        if last_error:
            messages.append({
                "role": "user",
                "content": (
                    "Your last reply failed validation: "
                    f"{last_error}. Reply again with JSON only, "
                    "matching the shape above."
                ),
            })

        # Call the LLM API
        try:
            response = httpx.post(
                LLM_API_URL,
                headers={
                    "Authorization": f"Bearer {settings.LLM_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.LLM_MODEL,
                    "messages": messages,
                    "temperature": 0,
                },
                timeout=30,
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise LLMRequestError(f"LLM API call failed: {e}")

        # Read the reply as JSON
        try:
            reply = response.json()["choices"][0]["message"]["content"]
            data = json.loads(reply)
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise LLMParseError(f"LLM reply was not valid JSON: {e}")

        # Check the reply against the invoice shape
        try:
            return ParsedInvoice(**data)
        except ValidationError as e:
            last_error = str(e)

    # Both attempts failed validation
    raise LLMParseError(
        f"LLM output failed validation after one retry: {last_error}"
    )
