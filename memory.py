mem_list = []
user_name = None

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


def set_user_name(name):
    global user_name
    user_name = name.strip() if isinstance(name, str) else None


def get_user_name():
    return user_name


def get_last_user_message():
    if len(mem_list) == 0:
        return None

    return mem_list[-1]["user"]
