from mcp.server.fastmcp import FastMCP
from src.services.story_service import StoryService
import os
from dotenv import load_dotenv
from typing import Union

# Load environment variables
load_dotenv(override=True)
print(f"RPC URL from env: {os.getenv('RPC_PROVIDER_URL')}")

# Get environment variables
private_key = os.getenv('WALLET_PRIVATE_KEY')
rpc_url = os.getenv('RPC_PROVIDER_URL')
if not private_key or not rpc_url:
    raise ValueError("WALLET_PRIVATE_KEY and RPC_PROVIDER_URL environment variables are required")

# Initialize Story service
story_service = StoryService(rpc_url=rpc_url, private_key=private_key)

# Initialize MCP
mcp = FastMCP("Story Protocol Server")

SPG_NFT_CONTRACT = os.getenv('SPG_NFT_CONTRACT', '0x58E2c909D557Cd23EF90D14f8fd21667A5Ae7a93')  # Default value

# Only register IPFS-related tools if IPFS is enabled
if story_service.ipfs_enabled:
    @mcp.tool()
    def upload_image_to_ipfs(image_data: Union[bytes, str]) -> str:
        """
        Upload an image to IPFS using Pinata API.
        
        Args:
            image_data: Either bytes of image data or URL to image
        
        Returns:
            str: IPFS URI of the uploaded image
        """
        try:
            ipfs_uri = story_service.upload_image_to_ipfs(image_data)
            return f"Successfully uploaded image to IPFS: {ipfs_uri}"
        except Exception as e:
            return f"Error uploading image to IPFS: {str(e)}"

    @mcp.tool()
    def create_nft_metadata(
        image_uri: str,
        name: str,
        description: str,
        attributes: list = None
    ) -> str:
        """
        Create and upload NFT metadata to IPFS.
        
        Args:
            image_uri: IPFS URI of the uploaded image
            name: Name of the NFT
            description: Description of the NFT
            attributes: Optional list of attribute dictionaries
        
        Returns:
            str: Result message with metadata details and IPFS URI
        """
        try:
            result = story_service.create_nft_metadata(
                image_uri=image_uri,
                name=name,
                description=description,
                attributes=attributes
            )
            return (
                f"Successfully created and uploaded NFT metadata:\n"
                f"Metadata URI: {result['metadata_uri']}\n"
                f"Metadata: {result['metadata']}"
            )
        except Exception as e:
            return f"Error creating NFT metadata: {str(e)}"

@mcp.tool()
def get_license_terms(license_terms_id: int) -> str:
    """Get the license terms for a specific ID."""
    try:
        terms = story_service.get_license_terms(license_terms_id)
        return f"License Terms {license_terms_id}: {terms}"
    except Exception as e:
        return f"Error retrieving license terms: {str(e)}"

@mcp.tool()
def mint_license_tokens(
    licensor_ip_id: str,
    license_terms_id: int,
    receiver: str = None,
    max_minting_fee: int = None,
    max_revenue_share: int = None
) -> str:
    """
    Mint license tokens for a specific IP and license terms.
    
    Args:
        licensor_ip_id: The IP ID to mint licenses for
        license_terms_id: The license terms ID to use
        receiver: Optional address to receive tokens (defaults to caller)
        max_minting_fee: Optional maximum minting fee
        max_revenue_share: Optional maximum revenue share percentage (0-100,000,000)
    """
    try:
        # Build kwargs dict with only provided parameters
        kwargs = {
            'licensor_ip_id': licensor_ip_id,
            'license_terms_id': license_terms_id,
            'amount': 1  # Hardcoded amount to 1
        }
        
        if receiver is not None:
            kwargs['receiver'] = receiver
        if max_minting_fee is not None:
            kwargs['max_minting_fee'] = max_minting_fee
        if max_revenue_share is not None:
            kwargs['max_revenue_share'] = max_revenue_share

        # Use the SPG NFT contract address from the environment variable
        kwargs['license_template'] = SPG_NFT_CONTRACT

        response = story_service.mint_license_tokens(**kwargs)
        
        return (
            f"Successfully minted license tokens:\n"
            f"Transaction Hash: {response['txHash']}\n"
            f"License Token IDs: {response['licenseTokenIds']}"
        )
    except ValueError as e:
        # Return specific validation errors
        return f"Validation error: {str(e)}"
    except Exception as e:
        return f"Error minting license tokens: {str(e)}"

@mcp.tool()
def send_ip(to_address: str, amount: float) -> str:
    """
    Send IP tokens to another address.
    
    :param to_address: The recipient's wallet address
    :param amount: Amount of IP tokens to send (1 IP = 1 Ether)
    :return: Transaction result message
    """
    try:
        response = story_service.send_ip(to_address, amount)
        return f"Successfully sent {amount} IP to {to_address}. Transaction hash: {response['txHash']}"
    except Exception as e:
        return f"Error sending IP: {str(e)}"

@mcp.tool()
def mint_and_register_ip_with_terms(
    spg_nft_contract: str,
    nft_metadata_uri: str,
    commercial_rev_share: int,
    derivatives_allowed: bool,
    recipient: str = None
) -> str:
    """
    Mint an NFT, register it as an IP Asset, and attach PIL terms.

    Args:
        spg_nft_contract: Address of the SPG NFT contract
        nft_metadata_uri: URI of the NFT metadata on IPFS
        commercial_rev_share: Percentage of revenue share (0-100)
        derivatives_allowed: Whether derivatives are allowed
        recipient: Optional recipient address (defaults to sender)

    Returns:
        str: Result message with transaction details
    """
    try:
        # Validate inputs
        if not (0 <= commercial_rev_share <= 100):
            raise ValueError("commercial_rev_share must be between 0 and 100")

        # Call service with simplified parameters
        response = story_service.mint_and_register_ip_with_terms(
            spg_nft_contract=spg_nft_contract,
            nft_metadata_uri=nft_metadata_uri,
            commercial_rev_share=commercial_rev_share,
            derivatives_allowed=derivatives_allowed,
            recipient=recipient
        )

        return (
            f"Successfully minted and registered IP asset with terms:\n"
            f"Transaction Hash: {response['txHash']}\n"
            f"IP ID: {response['ipId']}\n"
            f"Token ID: {response['tokenId']}\n"
            f"License Terms IDs: {response['licenseTermsIds']}"
        )
    except Exception as e:
        return f"Error minting and registering IP with terms: {str(e)}"

# @mcp.tool()
# def register_ip_asset(nft_contract: str, token_id: int, metadata: dict) -> str:
#     """
#     Register an NFT as an IP Asset.
    
#     :param nft_contract: NFT contract address
#     :param token_id: Token ID of the NFT
#     :param metadata: IP Asset metadata following Story Protocol standard
#     :return: Registration result message
#     """
#     try:
#         response = story_service.register_ip_asset(nft_contract, token_id, metadata)
#         return f"Successfully registered IP asset. IP ID: {response.get('ipId')}"
#     except Exception as e:
#         return f"Error registering IP asset: {str(e)}"

# @mcp.tool()
# def attach_license_terms(ip_id: str, license_terms_id: int) -> str:
#     """
#     Attach a licensing policy to an IP Asset.
    
#     :param ip_id: IP Asset ID
#     :param license_terms_id: License terms ID to attach
#     :return: Result message
#     """
#     try:
#         response = story_service.attach_license_terms(ip_id, license_terms_id)
#         return f"Successfully attached license terms {license_terms_id} to IP {ip_id}. Response: {response}"
#     except Exception as e:
#         return f"Error attaching license terms: {str(e)}"

# @mcp.tool()
# def mint_and_register_nft(to_address: str, metadata_uri: str, ip_metadata: dict) -> str:
#     """
#     Mint an NFT and register it as IP in one transaction.
    
#     :param to_address: Recipient's wallet address
#     :param metadata_uri: URI for the NFT metadata
#     :param ip_metadata: IP Asset metadata following Story Protocol standard
#     :return: Minting result message
#     """
#     try:
#         response = story_service.mint_and_register_nft(to_address, metadata_uri, ip_metadata)
#         return f"Successfully minted and registered NFT to {to_address}. Transaction details: {response}"
#     except Exception as e:
#         return f"Error minting and registering NFT: {str(e)}"

# @mcp.tool()
# def mint_generated_image(
#     image_data: Union[bytes, str],
#     name: str,
#     description: str,
#     recipient_address: str,
#     attributes: list = None,
#     ip_metadata: dict = None
# ) -> str:
#     """
#     Upload a generated image, mint it as an NFT, and register it as IP.
    
#     :param image_data: Either bytes of image data or URL to image
#     :param name: Name for the NFT
#     :param description: Description for the NFT
#     :param recipient_address: Address to receive the NFT
#     :param attributes: Optional list of NFT attributes
#     :param ip_metadata: Optional IP Asset metadata
#     :return: Result message with URIs and transaction details
#     """
#     try:
#         response = story_service.mint_generated_image(
#             image_data=image_data,
#             name=name,
#             description=description,
#             recipient_address=recipient_address,
#             attributes=attributes,
#             ip_metadata=ip_metadata
#         )
#         return (
#             f"Successfully processed generated image:\n"
#             f"Image URI: {response['image_uri']}\n"
#             f"Metadata URI: {response['metadata_uri']}\n"
#             f"Transaction Details: {response['transaction_details']}"
#         )
#     except Exception as e:
#         return f"Error processing generated image: {str(e)}"

# @mcp.tool()
# def register_non_commercial_social_remixing_pil() -> str:
#     """Register a non-commercial social remixing PIL license."""
#     try:
#         response = story_service.register_non_commercial_social_remixing_pil()
#         return f"Non-commercial social remixing PIL registered: {response}"
#     except Exception as e:
#         return f"Error registering non-commercial PIL: {str(e)}"

if __name__ == "__main__":
    mcp.run()
