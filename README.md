# AI Agent

A simple, modular AI agent built with SOLID principles.

## Project Structure

```
cpu-rizz/
├── api/
│   ├── __init__.py
│   ├── base.py          # Abstract API client interface
│   └── sambanova.py     # Sambanova implementation
├── config/
│   ├── __init__.py
│   └── settings.py      # Configuration management
├── tools/
│   ├── __init__.py
│   ├── base.py          # Abstract Tool interface
│   └── web_search.py    # Web search tool implementation
├── agent.py             # Agent with tool calling loop
├── main.py              # Example usage
├── requirements.txt     # Dependencies
└── .env.example         # Example environment variables
```

## SOLID Principles Applied

- **Single Responsibility**: Each class has one clear purpose
  - `SambanovaClient`: Handles Sambanova API communication
  - `Settings`: Manages configuration

- **Open/Closed**: Extend functionality without modifying existing code
  - Add new API providers by implementing `APIClient` abstract class

- **Liskov Substitution**: Any `APIClient` implementation can be swapped

- **Interface Segregation**: Small, focused interfaces
  - `APIClient` defines only essential chat method

- **Dependency Inversion**: Depend on abstractions
  - Code depends on `APIClient` interface, not concrete implementations

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file from example:
```bash
cp .env.example .env
```

3. Add your Sambanova API key to `.env`

## Usage

```python
from dotenv import load_dotenv
from api import SambanovaClient
from config import Settings

load_dotenv()

settings = Settings.from_env()
client = SambanovaClient(api_key=settings.api_key, model=settings.model)

messages = [
    {"role": "user", "content": "Hello!"}
]

response = client.chat(messages=messages)
print(response)
```

Run the example:
```bash
python main.py
```

## Adding New API Providers

To add a new provider, create a new class that inherits from `APIClient`:

```python
from api.base import APIClient

class NewProviderClient(APIClient):
    def chat(self, messages, **kwargs):
        # Implementation here
        pass
```
