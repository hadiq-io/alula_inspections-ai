from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing Azure OpenAI connection...")
print(f"Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT')}/openai/v1/")
print(f"Deployment: {os.getenv('AZURE_DEPLOYMENT_NAME')}")
print(f"API Key: {os.getenv('AZURE_OPENAI_KEY')[:10]}...")

try:
    client = OpenAI(
        base_url=f"{os.getenv('AZURE_OPENAI_ENDPOINT')}/openai/v1/",
        api_key=os.getenv("AZURE_OPENAI_KEY")
    )
    
    response = client.chat.completions.create(
        model=os.getenv("AZURE_DEPLOYMENT_NAME"),
        messages=[{"role": "user", "content": "Hello"}],
        max_completion_tokens=50  # Changed from max_tokens
    )
    
    print("\n✅ SUCCESS!")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
