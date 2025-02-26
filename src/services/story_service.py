from web3 import Web3
from story_protocol_python_sdk.story_client import StoryClient
import requests
import os
from typing import Union
import time
import json

class StoryService:
    def __init__(self, rpc_url: str, private_key: str):
        """Initialize Story Protocol service with RPC URL and private key."""
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        if not self.web3.is_connected():
            raise Exception("Failed to connect to the Web3 provider")

        self.account = self.web3.eth.account.from_key(private_key)
        self.client = StoryClient(web3=self.web3, account=self.account, chain_id=1315)
        
        # Add default license template
        self.LICENSE_TEMPLATE = "0x2E896b0b2Fdb7457499B56AAaA4AE55BCB4Cd316"
        
        # Initialize Pinata JWT
        self.pinata_jwt = os.getenv('PINATA_JWT')
        if not self.pinata_jwt:
            self.ipfs_enabled = False
            print("Warning: PINATA_JWT environment variable not found. IPFS functions will be disabled.")
        else:
            self.ipfs_enabled = True

    def get_license_terms(self, license_terms_id: int) -> dict:
        """Get the license terms for a specific ID."""
        response = self.client.License.getLicenseTerms(license_terms_id)
        if not response:
            raise ValueError(f"No license terms found for ID {license_terms_id}")
        
        return {
            'transferable': response[0],
            'royaltyPolicy': response[1],
            'defaultMintingFee': response[2],
            'expiration': response[3],
            'commercialUse': response[4],
            'commercialAttribution': response[5],
            'commercializerChecker': response[6],
            'commercializerCheckerData': response[7].hex() if isinstance(response[7], bytes) else response[7],
            'commercialRevShare': response[8],
            'commercialRevCeiling': response[9],
            'derivativesAllowed': response[10],
            'derivativesAttribution': response[11],
            'derivativesApproval': response[12],
            'derivativesReciprocal': response[13],
            'derivativeRevCeiling': response[14],
            'currency': response[15],
            'uri': response[16]
        }

    def mint_license_tokens(
        self,
        licensor_ip_id: str,
        license_terms_id: int,
        receiver: str = None,
        amount: int = 1,
        max_minting_fee: int = None,
        max_revenue_share: int = None
    ) -> dict:
        """
        Mint license tokens for a specific IP and license terms.
        
        Args:
            licensor_ip_id: The IP ID to mint licenses for
            license_terms_id: The license terms ID to use
            receiver: Address to receive the license tokens (defaults to caller)
            amount: Number of license tokens to mint (defaults to 1)
            max_minting_fee: Optional maximum minting fee
            max_revenue_share: Optional maximum revenue share percentage (0-100,000,000)
        """
        try:
            # Build kwargs dict with only provided parameters
            kwargs = {
                'licensor_ip_id': licensor_ip_id,
                'license_template': self.LICENSE_TEMPLATE,  # Use default template
                'license_terms_id': license_terms_id,
                'amount': amount,
                'receiver': receiver if receiver else self.account.address
            }
            
            if max_minting_fee is not None:
                kwargs['max_minting_fee'] = max_minting_fee
            if max_revenue_share is not None:
                kwargs['max_revenue_share'] = max_revenue_share

            response = self.client.License.mintLicenseTokens(**kwargs)
            return response

        except Exception as e:
            print(f"Error minting license tokens: {str(e)}")
            raise

    def send_ip(self, to_address: str, amount: float) -> dict:
        """
        Send IP tokens to a specified address using native token transfer.
        
        :param to_address: Recipient's address
        :param amount: Amount of IP tokens to send (1 IP = 1 Ether)
        :return: Transaction details
        """
        try:
            # Convert amount to Wei (1 IP = 1 Ether)
            value_in_wei = self.web3.to_wei(amount, 'ether')

            print(f"Debug: Account address: {self.account.address}")
            print(f"Debug: Network connected: {self.web3.eth.chain_id}")
            print(f"Debug: Account balance: {self.web3.eth.get_balance(self.account.address)}")

            # Set a default gas price if we can't get it from the network
            try:
                gas_price = self.web3.eth.gas_price
            except Exception:
                # Fallback gas price (50 gwei)
                gas_price = self.web3.to_wei(50, 'gwei')
            
            # Estimate gas limit for this transaction
            try:
                gas_estimate = self.web3.eth.estimate_gas({
                    'to': self.web3.to_checksum_address(to_address),
                    'from': self.account.address,
                    'value': value_in_wei
                })
            except Exception:
                # Fallback gas limit
                gas_estimate = 21000  # Standard transfer gas limit

            # Build the transaction with dynamic gas settings
            transaction = {
                'to': self.web3.to_checksum_address(to_address),
                'value': value_in_wei,
                'gas': gas_estimate,
                'gasPrice': gas_price,
                'nonce': self.web3.eth.get_transaction_count(self.account.address),
                'chainId': 1315  # Story Protocol chain ID
            }

            # Sign and send the transaction
            signed_txn = self.account.sign_transaction(transaction)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)

            # Wait for transaction receipt
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

            return {
                'txHash': tx_hash.hex(),
                'txReceipt': tx_receipt
            }
        except Exception as e:
            print(f"Error details: {str(e)}")
            print(f"Debug: Transaction details: {transaction}")
            raise

    def upload_image_to_ipfs(self, image_data: Union[bytes, str]) -> str:
        """Upload an image to IPFS using Pinata API"""
        if not self.ipfs_enabled:
            raise Exception("IPFS functions are disabled. Please provide PINATA_JWT environment variable.")
        
        try:
            # If image_data is a URL, download it first
            if isinstance(image_data, str) and image_data.startswith('http'):
                response = requests.get(image_data)
                image_data = response.content

            # Upload to Pinata
            headers = {
                'Authorization': f'Bearer {self.pinata_jwt}'
            }
            files = {
                'file': ('image.png', image_data, 'image/png')
            }
            
            response = requests.post(
                'https://api.pinata.cloud/pinning/pinFileToIPFS',
                files=files,
                headers=headers
            )

            if response.status_code != 200:
                raise Exception(f"Failed to upload to IPFS: {response.text}")

            return f"ipfs://{response.json()['IpfsHash']}"
        except Exception as e:
            print(f"Error uploading to IPFS: {str(e)}")
            raise

    def create_ip_metadata(
        self,
        image_uri: str,
        name: str,
        description: str,
        attributes: list = None
    ) -> dict:
        """
        Create both NFT and IP metadata and upload to IPFS
        
        Args:
            image_uri: IPFS URI of the uploaded image
            name: Name of the NFT/IP
            description: Description of the NFT/IP
            attributes: Optional list of attribute dictionaries
        Returns:
            dict: Both metadata URIs and their hashes
        """
        if not self.ipfs_enabled:
            raise Exception("IPFS functions are disabled. Please provide PINATA_JWT environment variable.")

        try:
            # Get image hash if it's a URL
            if image_uri.startswith('http'):
                image_hash = self._get_file_hash(image_uri)
            else:
                # For IPFS URIs, extract hash from URI
                image_hash = image_uri.replace('ipfs://', '')
            
            # Create NFT metadata (standard ERC721 format)
            nft_metadata = {
                "name": name,
                "description": description,
                "image": image_uri,
                "attributes": attributes or []
            }

            # Create IP metadata following Story Protocol standard
            ip_metadata = {
                "title": name,
                "description": description,
                "createdAt": int(time.time()),
                "image": image_uri,
                "imageHash": f"0x{image_hash}",  # Add 0x prefix
                "mediaUrl": image_uri,
                "mediaHash": f"0x{image_hash}",  # Same as imageHash since they point to same file
                "mediaType": "image/png"  # Adjust based on actual image type
            }

            # Upload NFT metadata to IPFS
            nft_response = requests.post(
                'https://api.pinata.cloud/pinning/pinJSONToIPFS',
                json=nft_metadata,
                headers={
                    'Authorization': f'Bearer {self.pinata_jwt}',
                    'Content-Type': 'application/json'
                }
            )
            if nft_response.status_code != 200:
                raise Exception(f"Failed to upload NFT metadata: {nft_response.text}")
            nft_metadata_uri = f"https://ipfs.io/ipfs/{nft_response.json()['IpfsHash']}"
            
            # Upload IP metadata to IPFS
            ip_response = requests.post(
                'https://api.pinata.cloud/pinning/pinJSONToIPFS',
                json=ip_metadata,
                headers={
                    'Authorization': f'Bearer {self.pinata_jwt}',
                    'Content-Type': 'application/json'
                }
            )
            if ip_response.status_code != 200:
                raise Exception(f"Failed to upload IP metadata: {ip_response.text}")
            ip_metadata_uri = f"https://ipfs.io/ipfs/{ip_response.json()['IpfsHash']}"

            # Generate hashes of the metadata JSONs
            nft_metadata_hash = self.web3.keccak(text=json.dumps(nft_metadata, sort_keys=True))
            ip_metadata_hash = self.web3.keccak(text=json.dumps(ip_metadata, sort_keys=True))

            # Create metadata structure for registration
            registration_metadata = {
                "ip_metadata_uri": ip_metadata_uri,
                "ip_metadata_hash": ip_metadata_hash.hex(),
                "nft_metadata_uri": nft_metadata_uri,
                "nft_metadata_hash": nft_metadata_hash.hex()
            }

            return {
                'nft_metadata': nft_metadata,
                'nft_metadata_uri': nft_metadata_uri,
                'nft_metadata_hash': nft_metadata_hash.hex(),
                'ip_metadata': ip_metadata,
                'ip_metadata_uri': ip_metadata_uri,
                'ip_metadata_hash': ip_metadata_hash.hex(),
                'registration_metadata': registration_metadata
            }

        except Exception as e:
            print(f"Error creating metadata: {str(e)}")
            raise

    async def _get_file_hash(self, url: str) -> str:
        """
        Get hash of a file from its URL using web3's keccak
        
        Args:
            url: URL of the image/media file
        Returns:
            str: Hash in hex format without 0x prefix
        """
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to download file: {response.text}")
        
        # Hash the raw bytes using web3's keccak
        file_hash = self.web3.keccak(response.content)
        return file_hash.hex()[2:]  # Remove 0x prefix

    def mint_and_register_ip_with_terms(
        self,
        spg_nft_contract: str,
        commercial_rev_share: int,
        derivatives_allowed: bool,
        registration_metadata: dict = None,
        recipient: str = None
    ) -> dict:
        """
        Mint an NFT, register it as an IP Asset, and attach PIL terms.
        
        Args:
            spg_nft_contract: Address of the SPG NFT contract
            nft_metadata_uri: URI of the NFT metadata on IPFS
            commercial_rev_share: Percentage of revenue share (0-100)
            derivatives_allowed: Whether derivatives are allowed
            registration_metadata: Optional dict containing full metadata structure
            recipient: Optional recipient address (defaults to sender)
        """
        try:
            # Create terms matching our working structure
            terms = [{
                'terms': {
                    'transferable': True,
                    'royalty_policy': "0xBe54FB168b3c982b7AaE60dB6CF75Bd8447b390E",
                    'default_minting_fee': 0,
                    'expiration': 0,
                    'commercial_use': commercial_rev_share > 0,
                    'commercial_attribution': False,
                    'commercializer_checker': "0x0000000000000000000000000000000000000000",
                    'commercializer_checker_data': "0x0000000000000000000000000000000000000000",
                    'commercial_rev_share': commercial_rev_share,
                    'commercial_rev_ceiling': 0,
                    'derivatives_allowed': derivatives_allowed,
                    'derivatives_attribution': derivatives_allowed,
                    'derivatives_approval': False,
                    'derivatives_reciprocal': derivatives_allowed,
                    'derivative_rev_ceiling': 0,
                    'currency': "0x1514000000000000000000000000000000000000",
                    'uri': ""
                },
                'licensing_config': {
                    'is_set': True,
                    'minting_fee': 0,
                    'hook_data': "",
                    'licensing_hook': "0x0000000000000000000000000000000000000000",
                    'commercial_rev_share': commercial_rev_share,
                    'disabled': False,
                    'expect_minimum_group_reward_share': 0,
                    'expect_group_reward_pool': "0x0000000000000000000000000000000000000000"
                }
            }]

            # Build kwargs for mintAndRegisterIpAssetWithPilTerms
            kwargs = {
                'spg_nft_contract': spg_nft_contract,
                'terms': terms,
                'recipient': recipient if recipient else self.account.address,
                'allow_duplicates': True
            }
            
            # Only add ip_metadata if registration_metadata is provided
            if registration_metadata:
                kwargs['ip_metadata'] = registration_metadata

            response = self.client.IPAsset.mintAndRegisterIpAssetWithPilTerms(**kwargs)

            return {
                'txHash': response.get('txHash'),
                'ipId': response.get('ipId'),
                'tokenId': response.get('tokenId'),
                'licenseTermsIds': response.get('licenseTermsIds')
            }

        except Exception as e:
            print(f"Error in mint_and_register_ip_with_terms: {str(e)}")
            raise

    # def register_pil_terms(
    #     self,
    #     transferable: bool = False,
    #     commercial_use: bool = False,
    #     derivatives_allowed: bool = False,
    #     default_minting_fee: int = 92
    # ) -> dict:
    #     """Register new PIL terms with customizable parameters."""
    #     response = self.client.License.registerPILTerms(
    #         transferable=transferable,
    #         royalty_policy=self.web3.to_checksum_address("0x0000000000000000000000000000000000000000"),
    #         default_minting_fee=default_minting_fee,
    #         expiration=0,
    #         commercial_use=commercial_use,
    #         commercial_attribution=False,
    #         commercializer_checker=self.web3.to_checksum_address("0x0000000000000000000000000000000000000000"),
    #         commercializer_checker_data="0x",
    #         commercial_rev_share=0,
    #         commercial_rev_ceiling=0,
    #         derivatives_allowed=derivatives_allowed,
    #         derivatives_attribution=False,
    #         derivatives_approval=False,
    #         derivatives_reciprocal=False,
    #         derivative_rev_ceiling=0,
    #         currency=self.web3.to_checksum_address("0x0000000000000000000000000000000000000000"),
    #         uri=""
    #     )
    #     return response

    # def register_non_commercial_social_remixing_pil(self) -> dict:
    #     """Register a non-commercial social remixing PIL license."""
    #     return self.client.License.registerNonComSocialRemixingPIL()

        #TODO: don't need this function for now
    # def register_ip_asset(self, nft_contract: str, token_id: int, metadata: dict) -> dict:
    #     """
    #     Register an NFT as an IP Asset with metadata
        
    #     :param nft_contract: NFT contract address
    #     :param token_id: Token ID of the NFT
    #     :param metadata: IP Asset metadata following Story Protocol standard
    #     :return: Transaction details
    #     """
    #     try:
    #         # Using the IPAsset module from the SDK
    #         response = self.client.IPAsset.registerRootIP(
    #             nftContract=self.web3.to_checksum_address(nft_contract),
    #             tokenId=token_id,
    #             metadata=metadata
    #         )
    #         return response
    #     except Exception as e:
    #         print(f"Error registering IP asset: {str(e)}")
    #         raise

    # def attach_license_terms(self, ip_id: str, license_terms_id: int) -> dict:
    #     """
    #     Attach a licensing policy to an IP Asset
        
    #     :param ip_id: IP Asset ID
    #     :param license_terms_id: License terms ID to attach
    #     :return: Transaction details
    #     """
    #     try:
    #         # Using the License module from the SDK
    #         response = self.client.License.addPolicyToIp(
    #             ipId=ip_id,
    #             licenseTermsId=license_terms_id
    #         )
    #         return response
    #     except Exception as e:
    #         print(f"Error attaching license terms: {str(e)}")
    #         raise
    #TODO: keep this function and test for now - pass in spg nft contract. image url -> upload to ipfs -> create metadata -> mint and register nft
    # def mint_and_register_nft(self, to_address: str, metadata_uri: str, ip_metadata: dict) -> dict:
    #     """
    #     Mint an NFT and register it as IP in one transaction
        
    #     :param to_address: Recipient's address
    #     :param metadata_uri: URI for the NFT metadata
    #     :param ip_metadata: IP Asset metadata following Story Protocol standard
    #     :return: Transaction details
    #     """
    #     try:
    #         # Using the IPAsset module's combined mint and register function
    #         response = self.client.IPAsset.mintAndRegisterRootIP(
    #             recipient=self.web3.to_checksum_address(to_address),
    #             tokenURI=metadata_uri,
    #             metadata=ip_metadata
    #         )
    #         return response
    #     except Exception as e:
    #         print(f"Error minting and registering NFT: {str(e)}")
    #         raise