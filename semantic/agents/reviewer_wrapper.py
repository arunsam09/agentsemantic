import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import AzureAISearchTool
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

def create_reviewer_agent():
    credential = DefaultAzureCredential()
    conn_str = os.getenv("AZURE_PROJECT_CONNECTION_STRING")
    project_client = AIProjectClient.from_connection_string(
        credential=credential,
        conn_str=conn_str
    )

    conn_list = project_client.connections._list_connections()["value"]
    conn_id = next(
        (conn["id"] for conn in conn_list if conn["properties"].get("metadata", {}).get("type", "").upper() == "AZURE_AI_SEARCH"),
        None
    )

    ai_search_tool = AzureAISearchTool(
        index_connection_id=conn_id,
        index_name=os.getenv("AZURE_INDEX_NAME"),
        query_type="Hybrid"
    )

    agent = project_client.agents.create_agent(
        model=os.getenv("AZURE_MODEL_NAME"),
        name=os.getenv("AZURE_AGENT_NAME"),
        instructions=os.getenv("AZURE_REVIEWER_INSTRUCTIONS"),
        tools=ai_search_tool.definitions,
        tool_resources=ai_search_tool.resources
    )

    return agent
