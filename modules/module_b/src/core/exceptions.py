"""
Custom exceptions for BatteryIQ suite.
"""

class BatteryIQException(Exception):
    """Base exception for all BatteryIQ domain errors."""
    pass

class ModelNotLoadedException(BatteryIQException):
    """Raised when an inference call is made before model weights are loaded."""
    pass

class InvalidTelemetryException(BatteryIQException):
    """Raised when incoming telemetry violates physics bounds or missing required keys."""
    pass

class DataProcessingException(BatteryIQException):
    """Raised when data transformation, windowing, or scaling fails."""
    pass

class ConfigurationException(BatteryIQException):
    """Raised when configuration files are missing or malformed."""
    pass
