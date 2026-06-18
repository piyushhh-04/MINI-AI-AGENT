mem_list = []

def add_to_memory(user_message, assistant_message):
    mem_list.append({"user": user_message, "assistant": assistant_message})

    if len(mem_list) > 5:
        mem_list.pop(0)


def get_memory_as_messages():
    messages = []
    for item in mem_list:
        messages.append({"role": "user", "content": item["user"]})
        messages.append({"role": "assistant", "content": item["assistant"]})
    return messages
