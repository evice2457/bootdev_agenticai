import argparse
import json
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

from functions.call_function import available_functions, call_function
from prompts import system_prompt


def main() -> None:
    # Load environment variables
    load_dotenv()

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set in the environment variables."
        )

    # Parse CLI arguments
    parser = argparse.ArgumentParser(description="AI Code Assistant")
    parser.add_argument(
        "user_prompt",
        type=str,
        help="Prompt to send to the LLM",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    args = parser.parse_args()

    # Create OpenAI client
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.user_prompt},
    ]

    # Send request
    for _ in range(20):
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=messages,
            tools=available_functions,
            temperature=0,
        )
        message = response.choices[0].message
        
        #Save assistant message into conversation history
        messages.append(message)

        if not response.usage:
            raise RuntimeError("API response appears to be malformed.")

        if args.verbose:
            print(f"User prompt: {args.user_prompt}")
            print(f"Prompt tokens: {response.usage.prompt_tokens}")
            print(f"Response tokens: {response.usage.completion_tokens}")

        message = response.choices[0].message

        # Normal text response --> stop program before hitting error
        if not message.tool_calls:
            print("Response:")
            print(message.content)
            return

        # Tool call response
        for tool_call in message.tool_calls:
            if tool_call.type != "function":
                continue

            function_args = json.loads(
                tool_call.function.arguments or "{}"
            )

            print(
                f"Calling function: "
                f"{tool_call.function.name}({function_args})"
            )
            result_message = call_function(tool_call, verbose=args.verbose)
            if result_message["content"] is None:
                raise Exception("Function call returned None, which is unexpected.")
            
            messages.append(result_message)
            
            if args.verbose:
                print(f"-> {result_message['content']}")
            
    print("Error: Agent reached maximum number of iterations.")
    sys.exit(1)

if __name__ == "__main__":
    main()