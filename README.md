# Story Protocol SDK MCP Server

This server provides MCP (Model Control Protocol) tools for interacting with Story Protocol's smart contracts through their Python SDK.

## Features

- Get license terms
- Register PIL terms with custom parameters
- Register non-commercial social remixing PIL licenses
- Mint license tokens

## Setup

1. Install dependencies using uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
```

2. Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env
```

Required environment variables:
- `WALLET_PRIVATE_KEY`: Your Ethereum wallet private key
- `RPC_PROVIDER_URL`: Your RPC provider URL
- `SPG_NFT_CONTRACT`: The address of the SPG NFT contract

3. Use inspector to test the server:
```bash
uv run mcp dev server.py
```

## Available Tools

1. `get_license_terms`: Retrieve license terms for a specific ID
2. `mint_license_tokens`: Mint license tokens for a specific IP and license terms
3. `send_ip`: Send IP tokens to a specified address using native token transfer
4. `upload_image_to_ipfs`: Upload an image to IPFS and return the URI
5. `create_nft_metadata`: Create NFT metadata for a specific image URI
6. `mint_and_register_ip_with_terms`: Mint and register an IP with terms

## Usage with MCP

You can use these tools with any MCP-compatible client. The tools are exposed through the MCP protocol and can be accessed using standard MCP clients.
