my_tasks = []

def add_task(task_name):
    if not isinstance(task_name, str) or not task_name.strip():
        return "Error: task_name must be a non-empty string"

    task_name = task_name.strip()
    my_tasks.append(task_name)
    return "Task added: " + task_name


def list_tasks():
    if len(my_tasks) == 0:
        return "No tasks yet."

    result = "Here are your tasks:\n"
    count = 1
    for task in my_tasks:
        result = result + str(count) + ". " + task + "\n"
        count = count + 1
    return result


tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Add a new task to the task list",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_name": {
                        "type": "string",
                        "description": "The task to add"
                    }
                },
                "required": ["task_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks that have been added so far",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


def run_tool(tool_name, tool_args):
    if tool_name == "add_task":
        task_name = tool_args.get("task_name", "")
        return add_task(task_name)

    elif tool_name == "list_tasks":
        return list_tasks()

    else:
        return "Error: unknown tool '" + str(tool_name) + "'"
