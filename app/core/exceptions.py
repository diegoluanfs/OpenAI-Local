class LocalLLMError(Exception):
    """Base exception for domain-specific failures."""


class ProviderUnavailableError(LocalLLMError):
    """Raised when the model provider is unavailable."""


class ModelNotFoundError(LocalLLMError):
    """Raised when a model is not installed or not found."""


class AuthenticationError(LocalLLMError):
    """Raised when API authentication fails."""
