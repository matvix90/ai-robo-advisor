AVAILABLE_MODELS = [
    # Anthropic Models
    {
        "provider": "anthropic",
        "model_name": "claude-3-5-sonnet-latest",
        "display": "Claude 3.5 Sonnet",
    },
    {
        "provider": "anthropic",
        "model_name": "claude-3-5-haiku-latest",
        "display": "Claude 3.5 Haiku",
    },
    # Google Models
    {
        "provider": "google_genai",
        "model_name": "gemini-2.0-flash",
        "display": "Gemini 2.0 Flash",
    },
    {
        "provider": "google_genai",
        "model_name": "gemini-2.5-flash",
        "display": "Gemini 2.5 Flash",
    },
    # OpenAI Models
    {"provider": "openai", "model_name": "gpt-4o", "display": "GPT-4o"},
    {"provider": "openai", "model_name": "gpt-4o-mini", "display": "GPT-4o Mini"},
    {"provider": "openai", "model_name": "gpt-3.5-turbo", "display": "GPT-3.5 Turbo"},
    # GROQ Models
    {
        "provider": "groq",
        "model_name": "llama-3.3-70b-versatile",
        "display": "Llama 3.3 70B Versatile (via Groq)",
    },
]
