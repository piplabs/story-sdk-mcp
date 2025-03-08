# Story MCP Hub

This repository serves as a central hub for Story Protocol's Model Context Protocol (MCP) servers. It provides a unified environment for running and managing various MCP services that enable AI agents to interact with Story Protocol's ecosystem.

## Project Structure

```
story-mcp-hub/
├── storyscan-mcp/       # MCP server for blockchain data queries via StoryScan 
├── story-sdk-mcp/       # MCP server for Story Protocol SDK interactions
├── utils/               # Shared utilities for MCP servers
├── .venv/               # Python virtual environment
├── pyproject.toml       # Project dependencies and configuration
├── .python-version      # Python version specification
└── README.md            # This file
```

```mermaid
graph TD
    subgraph "MCP Hub" 
        style MCP Hub fill:#F5F5FF,stroke:#9999CC,stroke-width:2px,rx:10,ry:10
        Agent["AI Agent<br>(Claude, IDEs, Tools)"]
        style Agent fill:#E6E6FA,stroke:#9370DB,stroke-width:2px,rx:8,ry:8
    end

    subgraph "StoryScan MCP Server"
        style StoryScan MCP Server fill:#F0F8FF,stroke:#87CEFA,stroke-width:2px,rx:10,ry:10
        StoryscanService["StoryScan Service"]
        style StoryscanService fill:#E6E6FA,stroke:#9370DB,stroke-width:2px,rx:8,ry:8
        
        subgraph "StoryScan Tools"
            style StoryScan Tools fill:#F0FFFF,stroke:#5F9EA0,stroke-width:2px,rx:10,ry:10
            StoryscanToolset["Balance & Stats<br>check_balance,<br>get_address_overview,<br>get_transactions,<br>interpret_transaction,<br>get_token_holdings,<br>get_nft_holdings,<br>get_stats"]
            style StoryscanToolset fill:#E0FFFF,stroke:#5F9EA0,stroke-width:2px,rx:8,ry:8
        end
    end

    subgraph "Story SDK MCP Server"
        style Story SDK MCP Server fill:#F5FFFA,stroke:#98FB98,stroke-width:2px,rx:10,ry:10
        StoryService["Story Service"]
        style StoryService fill:#E6E6FA,stroke:#9370DB,stroke-width:2px,rx:8,ry:8
        
        subgraph "Story SDK Tools"
            style Story SDK Tools fill:#F0FFF0,stroke:#90EE90,stroke-width:2px,rx:10,ry:10
            IPFSTools["IPFS Tools<br>upload_image_to_ipfs<br>create_ip_metadata"]
            style IPFSTools fill:#E0FFFF,stroke:#5F9EA0,stroke-width:2px,rx:8,ry:8
            IPTools["IP Management Tools<br>mint_and_register_ip_with_terms<br>get_license_terms,<br>mint_license_tokens,<br>send_ip,<br>create_spg_nft_collection"]
            style IPTools fill:#E0FFFF,stroke:#5F9EA0,stroke-width:2px,rx:8,ry:8
        end
    end

    subgraph "External Resources"
        style External Resources fill:#FFF0F5,stroke:#FFB6C1,stroke-width:2px,rx:10,ry:10
        IPFS[(IPFS/Pinata<br>Storage)]
        style IPFS fill:#FFE4E1,stroke:#DB7093,stroke-width:2px,rx:15,ry:15
        Blockchain[(Story Protocol<br>Blockchain)]
        style Blockchain fill:#E0F8E0,stroke:#90EE90,stroke-width:2px,rx:15,ry:15
        StoryScan[(StoryScan/Blockscout<br>API)]
        style StoryScan fill:#E6F3FF,stroke:#87CEFA,stroke-width:2px,rx:15,ry:15
    end

    Agent <--MCP Protocol--> StoryService
    Agent <--MCP Protocol--> StoryscanService
    StoryscanService --> StoryscanToolset
    StoryService --> IPFSTools
    StoryService --> IPTools
    
    StoryscanToolset <--API Calls--> StoryScan
    IPFSTools <--API Calls--> IPFS
    IPTools <--RPC Calls--> Blockchain
```

## MCP Servers

### StoryScan MCP Server
Provides tools for querying blockchain data, including address balances, transactions, and blockchain statistics.

**Tools:**
- `check_balance`: Check the balance of an address
- `get_transactions`: Get recent transactions for an address
- `get_stats`: Get current blockchain statistics
- `get_address_overview`: Get a comprehensive overview of an address
- `get_token_holdings`: Get all ERC-20 token holdings for an address
- `get_nft_holdings`: Get all NFT holdings for an address
- `interpret_transaction`: Get a human-readable interpretation of a transaction

### Story SDK MCP Server
Provides tools for interacting with Story Protocol's Python SDK.

**Tools:**
- `get_license_terms`: Retrieve license terms for a specific ID
- `mint_license_tokens`: Mint license tokens for a specific IP and license terms
- `send_ip`: Send IP tokens to a specified address using native token transfer
- `upload_image_to_ipfs`: Upload an image to IPFS and return the URI
- `create_ip_metadata`: Create NFT metadata for a specific image URI
- `mint_and_register_ip_with_terms`: Mint and register an IP with terms

## Setup

### Prerequisites
- Python 3.12+
- UV package manager

### Installation

1. Install UV package manager and install env:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone this repository:

```bash
git clone https://github.com/storyprotocol/story-mcp-hub.git
cd story-mcp-hub
```

3. Install dependencies using UV:

```bash
uv sync
```

4. Set up environment variables for each server:

For StoryScan MCP:
```bash
cd storyscan-mcp
cp .env.example .env
# Edit .env with your StoryScan API endpoint
```

For Story SDK MCP:
```bash
cd story-sdk-mcp
cp .env.example .env
# Edit .env with your wallet private key, RPC provider URL, etc.
```

## Running the Servers

### StoryScan MCP Server Inspector

```bash
cd storyscan-mcp
uv run mcp dev server.py
```

### Story SDK MCP Server

```bash
cd story-sdk-mcp
uv run mcp dev server.py
```

## Development

To add a new MCP server to the hub:

1. Create a new directory for your server
2. Implement the MCP protocol in your server
3. Add any necessary dependencies to the root `pyproject.toml`
4. Update this README with information about your server

## Troubleshooting

If you encounter issues:

1. Verify that environment variables are set correctly for each server
2. Check network connectivity to external APIs (StoryScan, IPFS, etc.)
3. Ensure you're using the correct Python version (3.12+)
4. Check that all dependencies are installed with `uv sync`

## License

[MIT License](LICENSE)
