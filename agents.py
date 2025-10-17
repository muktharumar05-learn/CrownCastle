import os
import docx
from autogen import GroupChat, GroupChatManager
from autogen.agentchat import UserProxyAgent, AssistantAgent

def read_text_file(file_path: str) -> str:
    """Reads content from a plain text file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def read_docx_file(file_path: str) -> str:
    """Reads content from a .docx file."""
    document = docx.Document(file_path)
    full_text = []
    for para in document.paragraphs:
        full_text.append(para.text)
    return '\n\n'.join(full_text)

# Define AutoGen Agents
user_proxy = UserProxyAgent(
    name="Admin",
    system_message="A human admin. Interact with the Creator Agent to generate lectures based on my instructions.",
    llm_config={"config_list": [{"model": "llama3", "base_url": "http://localhost:11434/v1", "api_key": "ollama"}]},
    human_input_mode="NEVER",
    is_termination_msg=lambda x: x.get("content", "") and "APPROVED" in x.get("content", "").upper(),
    code_execution_config={"work_dir": "coding", "use_docker": False}
)

creator_agent = AssistantAgent(
    name="Content_Agent",
    system_message="""You are an expert content creator. Your task is to generate a professional seminar lecture from raw text.
    You will be given the raw text and must use your knowledge and the provided tools to produce a high-quality lecture. I want it in PPT format.
    After drafting the lecture, you must send it to the Evaluator Agent for review.
    If the evaluation from the Evaluator Agent suggests revisions, you must incorporate that feedback into your next draft.
    You must always end your response by stating "APPROVED" or "NEEDS REVISION".
    """,
    llm_config={"config_list": [{"model": "llama3", "base_url": "http://localhost:11434/v1", "api_key": "ollama"}]},
)

evaluator_agent = AssistantAgent(
    name="Evaluator_Agent",
    system_message="""You are an expert evaluator. Your sole purpose is to review the lecture provided by the Content Agent.
    Based on your review, you must provide feedback or an approval.
    If the lecture is ready for a seminar, respond with a single word: "APPROVED".
    If the lecture needs improvement, respond with a single phrase: "NEEDS REVISION".
    You must not provide any other text.
    """,
    llm_config={"config_list": [{"model": "llama3", "base_url": "http://localhost:11434/v1", "api_key": "ollama"}]},
)


def run_lecture_agent(file_path: str):
    """
    Runs the lecture-generating agent with the provided text file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at: {file_path}")

    # Determine file type and read content accordingly
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension == '.txt':
        content = read_text_file(file_path)
    elif file_extension == '.docx':
        content = read_docx_file(file_path)
    else:
        raise ValueError("Unsupported file type. Please provide a .txt or .docx file.")

    print(f"Starting multi-agent lecture creation for file: {file_path}")

    # Set up the AutoGen group chat manager
    config_list = [
        {
            "model": "llama3",
            "base_url": "http://localhost:11434/v1",
            "api_key": "ollama",
        }
    ]
    
    
    groupchat = GroupChat(
        agents=[user_proxy, creator_agent, evaluator_agent],
        messages=[],
        max_round=20,
        speaker_selection_method="round_robin"
    )
    manager = GroupChatManager(groupchat=groupchat, llm_config={"config_list": config_list})

    # Define the initial task for the group chat
    task = f"""
    Content Agent, your task is to create a professional seminar lecture from the following raw text.
    Raw Text:
    {content}
    """

    # Initiate the group chat conversation
    chat_result = user_proxy.initiate_chat(
        manager,
        message=task,
        clear_history=True,
    )
    
    # You can access the final message content from the chat_result
    final_message = ""
    for msg in chat_result.chat_history:
        # Assuming the creator agent's final message contains the full lecture before the 'APPROVED' message from the evaluator
        if msg["name"] == creator_agent.name:
            final_message = msg["content"]
            
    if not final_message:
        print("Error: Could not retrieve final lecture content from chat history.")
        return
    
    # Save the final message to a file
    output_filename = "lecture_output.txt"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(final_message)
    
    print(f"\n---FINAL LECTURE GENERATION COMPLETE---\n")
    print(f"The final lecture has been saved to: {output_filename}")

if __name__ == "__main__":

    temp_file_path = "sample_text.txt"

    run_lecture_agent(temp_file_path)