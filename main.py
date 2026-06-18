import os
import json
from dotenv import load_dotenv
from openai import OpenAI

import memory
import tools

load_dotenv()

my_api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("GROQ_API_KEY")

if my_api_key is None:
    print("Error: OPENAI_API_KEY (or GROQ_API_KEY) not found. Please set it as an environment variable.")
    exit()

ai_client = OpenAI(
    api_key=my_api_key,
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "llama-3.1-8b-instant"


def ask_model(user_input):
    msgs = []
    msgs.append({
        "role": "system",
        "content": (
            "You are a helpful assistant. "
            "Use tools when they are useful for the user's request."
        )
    })

    old_msgs = memory.get_memory_as_messages()
    for m in old_msgs:
        msgs.append(m)

    msgs.append({"role": "user", "content": user_input})

    try:
        resp = ai_client.chat.completions.create(
            model=MODEL,
            messages=msgs,
            tools=tools.tools_schema
        )
    except Exception as e:
        print("Error: could not reach the API. Details:", e)
        return "Sorry, something went wrong while contacting the AI."

    reply = resp.choices[0].message

    while reply.tool_calls:
        msgs.append(reply)

        for tcall in reply.tool_calls:
            tname = tcall.function.name

            try:
                targs = json.loads(tcall.function.arguments or "{}")
                if not isinstance(targs, dict):
                    targs = {}
            except Exception:
                targs = {}

            try:
                tresult = tools.run_tool(tname, targs)
            except Exception as tool_error:
                tresult = "Error: tool execution failed: " + str(tool_error)

            msgs.append({
                "role": "tool",
                "tool_call_id": tcall.id,
                "content": tresult
            })

        try:
            resp = ai_client.chat.completions.create(
                model=MODEL,
                messages=msgs,
                tools=tools.tools_schema
            )
            reply = resp.choices[0].message
        except Exception as e:
            print("Error: could not reach the API. Details:", e)
            return "Sorry, something went wrong while contacting the AI after tool execution."

    return reply.content or ""


def extract_info(user_input):
    instruction = (
        "Extract the following information from the text and return ONLY "
        "valid JSON, with no extra words, no markdown, just the JSON object. "
        "Use this format: {\"name\": \"\", \"age\": 0, \"city\": \"\"}\n\n"
        "Text: " + user_input
    )

    try:
        resp = ai_client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You only output valid JSON. Nothing else."},
                {"role": "user", "content": instruction}
            ],
            response_format={"type": "json_object"}
        )
    except Exception:
        try:
            resp = ai_client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You only output valid JSON. Nothing else."},
                    {"role": "user", "content": instruction}
                ]
            )
        except Exception as e:
            print("Error: could not reach the API. Details:", e)
            return None

    raw = resp.choices[0].message.content

    try:
        parsed = json.loads(raw)
        return parsed
    except Exception:
        print("Error: model did not return valid JSON. Raw output below:")
        print(raw)
        return None


def handle_task_command(user_input):
    text = user_input.strip()
    lower_text = text.lower()

    if lower_text.startswith("list tasks"):
        return tools.list_tasks()

    if lower_text.startswith("add task"):
        task_text = text[8:].strip()

        if task_text.startswith("of "):
            task_text = task_text[3:].strip()
        elif task_text.startswith("to "):
            task_text = task_text[3:].strip()
        elif task_text.startswith("for "):
            task_text = task_text[4:].strip()

        if not task_text:
            return "Error: please type a task after add task"

        return tools.add_task(task_text)

    return None


def main():
    print("Mini AI Agent (type 'quit' to exit)")
    print("Use /extract <text> for structured JSON extraction")
    print("-" * 40)

    while True:
        try:
            user_input = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input.strip():
            continue

        if user_input.lower() == "quit":
            print("Goodbye!")
            break

        task_reply = handle_task_command(user_input)
        if task_reply is not None:
            print(task_reply)
            memory.add_to_memory(user_input, task_reply)
            continue

        if user_input.lower().startswith("/extract"):
            text_to_extract = user_input[len("/extract"):].strip()
            if not text_to_extract:
                print("Error: please provide text after /extract")
                continue
            result = extract_info(text_to_extract)
            if result is not None:
                print(json.dumps(result, indent=2))
                memory.add_to_memory(user_input, json.dumps(result))
            else:
                memory.add_to_memory(user_input, "Error: extraction failed")
            continue

        assistant_reply = ask_model(user_input)
        print("Assistant:", assistant_reply)

        memory.add_to_memory(user_input, assistant_reply)


if __name__ == "__main__":
    main()