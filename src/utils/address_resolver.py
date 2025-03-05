import requests
from web3 import Web3
from typing import Optional, Union


class AddressResolver:
    """
    Utility class for resolving addresses from domain names and vice versa.
    Implements a simple chain of responsibility pattern for address resolution.
    """
    
    def __init__(self, web3: Web3, chain_id: int = 1514):
        """
        Initialize the address resolver.
        
        Args:
            web3: Web3 instance for address validation and formatting
            chain_id: Chain ID for the blockchain (default: 1514 for Story Protocol)
        """
        self.web3 = web3
        self.chain_id = chain_id
        self.space_id_api_url = "https://nameapi.space.id"
    
    def resolve_address(self, address_or_domain: str) -> str:
        """
        Resolve a domain name to an address or return the address if it's already in address format.
        Implements a chain of responsibility: first check if it's an address, then try to resolve as domain.
        
        Args:
            address_or_domain: Either an Ethereum address (0x...) or a domain name (name.ip)
            
        Returns:
            str: The resolved Ethereum address
            
        Raises:
            ValueError: If the address cannot be resolved
        """
        # First handler: Check if it's already an address
        if self._is_ethereum_address(address_or_domain):
            return self.web3.to_checksum_address(address_or_domain)
            
        # Second handler: Try to resolve as a domain name
        resolved_address = self._resolve_domain_to_address(address_or_domain)
        if resolved_address:
            return self.web3.to_checksum_address(resolved_address)
            
        # If we get here, we couldn't resolve the address
        raise ValueError(f"Could not resolve address or domain: {address_or_domain}")
    
    def get_domain_for_address(self, address: str) -> Optional[str]:
        """
        Get the primary domain name for an address.
        
        Args:
            address: Ethereum address
            
        Returns:
            str: The domain name or None if not found
        """
        try:
            # Ensure address is in correct format
            address = self.web3.to_checksum_address(address)
            
            # Query Space ID API
            response = requests.get(
                f"{self.space_id_api_url}/getName?chainid={self.chain_id}&address={address}"
            )
            
            if response.status_code != 200:
                return None
                
            data = response.json()
            
            if data.get('code') != 0:
                return None
                
            return data.get('name')
            
        except Exception:
            return None
    
    def _is_ethereum_address(self, value: str) -> bool:
        """Check if a string is a valid Ethereum address."""
        if not isinstance(value, str):
            return False
        return value.startswith('0x') and len(value) == 42 and self.web3.is_address(value)
    
    def _resolve_domain_to_address(self, domain: str) -> Optional[str]:
        """Resolve a domain name to an address using Space ID API."""
        try:
            # Make request to Space ID API
            response = requests.get(f"{self.space_id_api_url}/getAddress?domain={domain}")
            
            if response.status_code != 200:
                return None
                
            data = response.json()
            
            if data.get('code') != 0:
                return None
                
            return data.get('address')
            
        except Exception:
            return None


# Create a convenience function for easy importing
def create_address_resolver(web3: Web3, chain_id: int = 1514) -> AddressResolver:
    """
    Create an AddressResolver instance.
    
    Args:
        web3: Web3 instance
        chain_id: Chain ID for the blockchain (default: 1514 for Story Protocol)
        
    Returns:
        AddressResolver: An instance of the AddressResolver
    """
    return AddressResolver(web3, chain_id) 