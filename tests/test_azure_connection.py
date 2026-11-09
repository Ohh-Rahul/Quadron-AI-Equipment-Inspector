
import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# Load configuration from .env
load_dotenv()

endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
agent_name = os.getenv("FOUNDRY_AGENT_NAME")

if not endpoint or not agent_name:
    raise ValueError("Missing Foundry endpoint or agent name in .env")

try:
    print("Connecting to Azure AI Foundry...")

    credential = DefaultAzureCredential()

    with AIProjectClient(
        endpoint=endpoint,
        credential=credential,
        allow_preview=True
    ) as project_client:

        openai_client = project_client.get_openai_client(
            agent_name=agent_name
        )

        print("Connected! Sending test message...")

        response = openai_client.responses.create(
            input="Briefly introduce yourself and explain your role in the Lab Equipment Condition Inspector project."
        )

        print("\n--- AGENT RESPONSE ---")
        print(response.output_text)
        print("\nAzure AI Foundry connection successful!")

except Exception as error:
    print("\nConnection failed.")
    print("Error:", error)
    raise
