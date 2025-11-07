# BCS-OUK Gen AI Seminar — Project Repository

This repository contains course work and practical exercises for the BCS-OUK Generative AI Seminar. It holds Jac and Python & Jac experiments, projects and assignment solutions made while learning generative models and integrating them with local tooling.
The Jaseci - OUK Generative AI Bootcamp focuses on building practical applications using Jac and byllm backends. The code in this repo demonstrates: building simple CLI apps with Jac, integrating LLMs for hint generation and interactive experiences, and testing LLM APIs.

## Project structure

```
Gen.AI/
├── code/                               # All JAC source code projects & MCP-Chatbot
│   ├── guess_game5.jac                 # Guessing game version 5 (JAC interface)
│   ├── guess_game5.impl.jac            # Fixed Implementation of Guessing game version 5
│   ├── guess_game6.jac                 # AI-enhanced guessing game (ByLLM-powered version)
│   ├── guess_game6.impl.jac            # Fixed Implementation of AI-enhanced guessing game
│   ├── mental_health_buddy.jac         # My project Mental health buddy chatbot interface (JAC)
│   ├── mental_health_buddy.impl.jac    # My project Mental health buddy chatbot implementation
│   ├── requirements.txt                # Python dependencies for `code/` subprojects
│   ├── .env                            # (NOT tracked) API keys and environment secrets
|   ├── .gitignore                      # Specific to code/ (redundant with root .gitignore)
│   ├── README.md                       # Documentation and usage guide for the `code/` directory
|   |
|   ├── MCP-Chatbot/                    # JAC-based MCP (Model Context Protocol) Chatbot
|   |   ├── Makefile                    # Automates Google API credential setup (Gemini API Key) for MCP Chatbot
│   |   ├── client.jac                  # Client logic for chatbot requests
│   |   ├── mcp_client.jac              # Handles client connection setup for MCP communication
│   |   ├── mcp_server.jac              # Main MCP server definition
│   |   ├── server.jac                  # Core server architecture for chatbot
│   |   ├── server.impl.jac             # Implementation logic for the server
│   |   ├── tools.jac                   # Utility tools and helper functions used by the MCP chatbot
│
├── codebase_genius/                    # AI-driven code understanding and documentation project
│   ├── .env                            # (NOT tracked) Project-specific environment variables & secrets
│   ├── .gitignore                      # Specific to codebase_genius/ (redundant with root .gitignore)
│   ├── requirements.txt                # Python & Jac dependencies for codebase_genius
│   ├── README.md                       # Overview & usage instructions for codebase_genius project
│   │
│   ├── BE/                             # Backend: JAC agents for repository mapping, analysis, and documentation
│   │   ├── utils.jac                   # Shared utility functions used across backend agents
│   │   ├── main.jac                    # Main supervisor architecture definition
│   │   ├── main.impl.jac               # Implementation of supervisor logic and repo handling
│   │   └── README.md                   # Documentation for the backend architecture
│   │
│   ├── FE/                             # Frontend: Streamlit app for user interface
│   │   ├── app.py                      # Python frontend entry point connecting to backend via API
│   │   └── README.md                   # Frontend setup, usage, and contribution guide
│
├── .gitignore                          # Global ignore rules for all subprojects (secrets, venv, chroma, etc.)
└── README.md                           # Main repository overview, course/project description, and reference links
	
```

## Important links

* Assignment 1 and examples and my project live in the `code/` folder: 
    - Completed assignment of guess_game5 [code/guess_game5.impl.jac](code/guess_game5.impl.jac)
    - Completed assignment of guess_game6 [code/guess_game6.impl.jac](code/guess_game6.impl.jac)
    - My project [code/mental_health_buddy.jac](code/mental_health_buddy.jac) and [code/mental_health_buddy.impl.jac](code/mental_health_buddy.impl.jac)

    -  See [code/README.md](code/README.md) for run instructions, usage, and expected output screenshots.

* Assignment 2 and my project live in the `codebase_genius/` folder:

    -  See [codebase_genius//README.md](codebase_genius//README.md) for run overview, usage, and live demonstration.
