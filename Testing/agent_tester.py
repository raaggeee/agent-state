import os
import pytest
import scenario
from langchain_openai import AzureChatOpenAI


def create_custom_openai_client():
    """
    Creates an OpenAI client configured for Azure API Management.

    This function demonstrates how to customize the OpenAI client for:
    1. Custom base URLs (e.g., Azure APIM endpoint)
    2. API versioning via query parameters
    3. Custom authentication headers (instead of standard Bearer tokens)

    Example environment variables (customize names as needed):
    - AZURE_GATEWAY_API_BASE: The full base URL of your Azure APIM endpoint (e.g., "https://my-gateway.azure-api.net")
    - AZURE_GATEWAY_API_VERSION: Azure OpenAI API version (e.g., "2024-05-01-preview")
    - AZURE_GATEWAY_HEADER_KEY_NAME: The name of the auth header (e.g., "Ocp-Apim-Subscription-Key")
    - AZURE_GATEWAY_HEADER_KEY_VALUE: The actual API key/subscription key value (e.g., "1234567890")

    Note: These variable names are suggestions only - use whatever fits your setup.

    Returns:
        OpenAI: Configured client instance for use with UserSimulatorAgent and JudgeAgent
    """
    # Load gateway configuration from environment
    # Customize these environment variable names to match your infrastructure
    base_url = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    # header_key_name = os.getenv("AZURE_GATEWAY_HEADER_KEY_NAME")
    header_key_value = os.getenv("AZURE_OPENAI_API_KEY")
    model_name = "gpt-5.4-nano"
    deployment_name = "gpt-5.4-nano"

    # Debug logging to verify configuration (helpful for troubleshooting)
    print(f"base_url: {base_url}")
    # print(f"header_key_name: {header_key_name}")
    print(f"header_key_value: {header_key_value}")
    print(f"api_version: {api_version}")

    # Create OpenAI client with custom configuration
    # The OpenAI SDK is flexible and allows overriding:
    # - base_url: Route requests through your gateway instead of api.openai.com
    # - default_query: Add query params to every request (needed for Azure API versioning)
    # - default_headers: Set custom auth headers (APIM, proxy credentials, etc.)
    return AzureChatOpenAI(
        model_name=model_name,
        azure_deployment=deployment_name,
        azure_endpoint=base_url,
        api_key=header_key_value,
        temperature=0,
        api_version="2024-12-01-preview",
    )


@pytest.mark.agent_test
@pytest.mark.asyncio
async def test_agent():
    custom_client = create_custom_openai_client()

    class Agent(scenario.AgentAdapter):
        async def call(self, input: scenario.AgentInput) -> scenario.AgentReturnTypes:
            print(input.messages)
            return agent.run(input.messages)
        

    result = await scenario.run(
        name="random_agent_tester",
        description="A user centric agent.",
        agents=[
            Agent(),
            scenario.UserSimulatorAgent(model="gpt-5.4-nano", client=custom_client),
            scenario.JudgeAgent(criteria=[
            # Behavior
            "Agent should not ask more than two follow-up questions per turn",
            
            # Ephemeral state
            "Agent should use ephemeral state for intermediate reasoning or scratch work and never expose it in the final response",
            
            # Session state
            "Agent should store conversation context (e.g. current task, recent decisions) in session state and use it across turns within the same session",
            "Agent should not re-ask information the user already provided earlier in the same session",
            
            # Persistent state
            "Agent should save user preferences (e.g. name, language, tone) to persistent state and recall them in future sessions without asking again",
            "Agent should update persistent state when the user explicitly changes a preference, without requiring a restart",
            
            # State integrity
            "Agent should never leak ephemeral or session data into persistent state unless explicitly instructed by the user",
            "Agent should gracefully handle missing or expired state by asking the user or falling back to a safe default, never failing silently",
        ],
        model="gpt-5.4-nano",
        api_key=os.getenv("AZURE_OPENAI_API_KEY"))
        ]
    )

    assert result.success