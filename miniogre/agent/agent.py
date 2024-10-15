import os
from typing import List, Dict, Any, Callable
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_community.tools import ShellTool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, MessagesState
from langgraph.prebuilt import ToolNode
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph, MessagesState
from langgraph.prebuilt import tools_condition, ToolNode

from dotenv import load_dotenv

load_dotenv()

# Define tools using the @tool decorator

@tool
def save_commands(commands: List[str]) -> str:
    """Saves the script commands to a file named commands.sh."""
    print(os.path.join(os.getcwd(), "commands.sh"))
    with open(os.path.join(os.getcwd(), "commands.sh"), "w") as file:
        for command in commands:
            file.write(command + "\n")
    return "Commands have been saved to commands.sh."

@tool
def save_dockerfile(content: str) -> str:
    """Saves the Dockerfile content to a file named 'Dockerfile'."""
    with open('Dockerfile', 'w') as f:
        f.write(content)
    return "Dockerfile has been saved to 'Dockerfile'."

@tool
def shell_command(command: str) -> str:
    """Executes a shell command and returns the output."""
    import subprocess
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error executing command: {e.stderr.strip()}"

@tool
def read_file(file_path: str) -> str:
    """Reads the content of a file and returns it."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File {file_path} not found."

@tool
def check_file_exists(file_path: str) -> str:
    """Checks if a file exists and returns detailed information."""
    import os

    # Normalize the path to handle any potential issues with separators
    normalized_path = os.path.normpath(file_path)

    # Check if the file exists
    exists = os.path.isfile(normalized_path)

    # Get additional information
    abs_path = os.path.abspath(normalized_path)
    dir_exists = os.path.isdir(os.path.dirname(normalized_path))

    result = f"File '{normalized_path}':\n"
    result += f"- Exists: {'Yes' if exists else 'No'}\n"
    result += f"- Absolute path: {abs_path}\n"
    result += f"- Parent directory exists: {'Yes' if dir_exists else 'No'}\n"
    result += f"- Current working directory: {os.getcwd()}"

    return result

@tool
def build_docker_image(dockerfile_path: str, image_name: str) -> str:
    """Builds a Docker image from the specified Dockerfile."""
    import subprocess
    try:
        result = subprocess.run(
            f"docker build -t {image_name} -f {dockerfile_path} .",
            shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return f"Docker image '{image_name}' built successfully.\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"Error building Docker image: {e.stderr}"

@tool
def run_docker_container(image_name: str, container_name: str, port_mapping: str = "") -> str:
    """Runs a Docker container from the specified image."""
    import subprocess
    port_option = f"-p {port_mapping}" if port_mapping else ""
    try:
        result = subprocess.run(
            f"docker run -d --name {container_name} {port_option} {image_name}",
            shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return f"Docker container '{container_name}' started successfully.\nContainer ID: {result.stdout.strip()}"
    except subprocess.CalledProcessError as e:
        return f"Error running Docker container: {e.stderr}"

# Define the tools to be used in the workflow
tools = [shell_command, save_commands, read_file, check_file_exists, save_dockerfile, build_docker_image]

def initalize_llm(provider: str, tools: List[Callable] = tools):
        if provider == "openai":
            try:
                model = os.getenv("OPENAI_MODEL", 'gpt-4o-mini')
            except:
                model = "gpt-4o-mini"
            llm = ChatOpenAI(model=model)
        # elif provider == "gemini":
        #     try:
        #         model = os.getenv("GEMINI_MODEL", 'gemini')
        #     except:
        #         model = "gemini"
        #     llm = ChatGoogleGenerativeAI(model=model)

        llm_with_tools = llm.bind_tools(tools)

        return llm_with_tools

def agent(path: str, provider: str):
    # Check if the ./commands.sh file exists
    if os.path.exists("./commands.sh"):
        os.remove("./commands.sh")

    # Define the system message
    sys_msg = SystemMessage(content="""You are a helpful software engineer tasked with preparing to run a Python script and containerize it. 
Your goal is to analyze the script's file path, determine any dependencies or environment setup needed, and provide the necessary commands to:
1. Create a virtual environment.
2. Activate the virtual environment.
3. Install dependencies.
4. Run the script successfully. This is the most complicated part; you should take into account the script's requirements and the system's configuration. Make sure to include command arguments if needed, as well as environment variables. Don't forget about environment variables.
5. Create a Dockerfile to containerize the application.
6. Build the Docker image.
You will save the commands to a bash script file named 'commands.sh' using the 'save_commands' tool, and save the Dockerfile content to 'Dockerfile' using the 'save_dockerfile' tool. Remind the user to run chmod +x commands.sh to make the file executable.

You can use shell commands to interact with the system and tools to read file contents, check file existence, save files, build Docker images. Always think step-by-step and explain your reasoning. 

Your output will be displayed to the user on the console, so make sure it's clear and easy to follow. No Markdown or HTML is needed, just plain text.

Never ask the user for any input or feedback; you finish once every command needed to run the file is saved, and you tried to build the Docker image.""")

    llm_with_tools = initalize_llm(provider, tools)

    # Node
    def assistant(state: MessagesState):
        print("Agent Message: ", state["messages"][-1].content[:300])
        return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

    # Build graph
    builder = StateGraph(MessagesState)
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges(
        "assistant",
        # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
        # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
        tools_condition,
    )
    builder.add_edge("tools", "assistant")

    # Compile graph
    graph = builder.compile()

    initial_state = {"messages": [HumanMessage(content=f'Help me run this file: {path}')]}

    response = graph.invoke(initial_state)

    for message in response["messages"]:
        message.pretty_print()

    return response


# Usage Example
if __name__ == "__main__":
    python_file_path = "path/to/file.py"

    response = agent(python_file_path, "openai")
