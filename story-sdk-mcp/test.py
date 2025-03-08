from dotenv import load_dotenv
from services.story_service import StoryService

# Load environment variables
load_dotenv()

# Initialize service
story_service = StoryService(
    rpc_url="https://mainnet.storyrpc.io",
    private_key="e432d83208d8575baf3b53b37077fca1e41e8d2e1587d127d6e43e90ed1e800a"
)

try:
    # Send 0.01 IP
    result = story_service.send_ip(
        to_address="0xCC11929EAf89E9266296ba01448eB7371b318fA2",
        amount=0.01
    )
    print(f"Transaction hash: {result['txHash']}")
    print(f"Full receipt: {result['txReceipt']}")
except Exception as e:
    print(f"Failed to send transaction: {str(e)}")