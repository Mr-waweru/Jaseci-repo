# BCS-OUK Gen AI Seminar — Project Repository

This repository contains course work and practical exercises for the BCS-OUK Generative AI Seminar. It holds Jac and Python & Jac experiments, projects and assignment solutions made while learning generative models and integrating them with local tooling.
The seminar focuses on building practical applications using Jac and popular LLM backends. The code in this repo demonstrates: building simple CLI apps with Jac, integrating LLMs for hint generation and interactive experiences, and testing LLM APIs.

## Project structure

```
Gen.AI/
├── code/                               # All source code
│   ├── guess_game5.jac                 # Guessing game5
│   ├── guess_game5.impl.jac            # Fixed guessing game5 impl.jac file
│   ├── guess_game6.jac                 # Guessing game6 AI-enhanced guessing game (byLLM)
│   ├── guess_game6.impl.jac            # Fixed guessing game6 AI-enhanced guessing game (byLLM)
│   ├── mental_health_buddy.jac         # My project Jac mental health buddy interface
│   ├── mental_health_buddy.impl.jac    # My project Jac mental health buddy implementation
│   ├── requirements.txt                # Requirements dependencies
│   ├── .env                            # (NOT tracked) API keys and secrets
│   └── README.md                       # Detailed instructions & usage for code
├── MCP-Chatbot/
│   ├── client.jac                      #
│   ├── mcp_client.jac                  #
│   ├── mcp_server.jac                  #
│   ├── server.jac                      #
│   ├── server.impl.jac                 #
│   ├── tools.jac                       #
├── .gitignore      
├── Makefile                            # Automate Google Credentials (Gemini API Key) on the terminal used in the MCP Chatbot    
└── README.md                           # course description + links 	
```

## Important links

* Assignment 1 and examples and my project live in the `code/` folder: 
    - Completed assignment of guess_game5 [code/guess_game5.impl.jac](code/guess_game5.impl.jac)
    - Completed assignment of guess_game6 [code/guess_game6.impl.jac](code/guess_game6.impl.jac)
    - My project [code/mental_health_buddy.jac](code/mental_health_buddy.jac) and [code/mental_health_buddy.impl.jac](code/mental_health_buddy.impl.jac)

    -  See [code/README.md](code/README.md) for run instructions, usage, and expected output screenshots.
