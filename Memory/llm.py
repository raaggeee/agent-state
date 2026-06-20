from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

load_dotenv()

endpoint = "https://himan-mn1s2e7k-eastus2.cognitiveservices.azure.com/"

model_name = "gpt-5.4-nano"
deployment_name = "gpt-5.4-nano"

# model_name = "gpt-5-nano"
# deployment_name = "gpt-5-nano"
llm = AzureChatOpenAI(
    model_name=model_name,
    azure_deployment=deployment_name,
    azure_endpoint=endpoint,
    temperature=0,
    api_version="2024-12-01-preview",
)
