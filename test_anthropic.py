import os
import sys

from anthropic import Anthropic
from dotenv import load_dotenv


def main() -> None:
    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")

    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY was not found in .env")
        sys.exit(1)

    client = Anthropic(api_key=api_key)

    try:
        response = client.messages.create(
            model=model,
            max_tokens=200,
            system="You are a QE assistant.",
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Reply with exactly: "
                        "Anthropic connection successful."
                    ),
                }
            ],
        )

        text = "".join(
            block.text
            for block in response.content
            if block.type == "text"
        )

        print(text)

    except Exception as exc:
        print(f"Anthropic connection failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()