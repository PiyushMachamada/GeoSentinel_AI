"""
GeoSentinel Custom Exceptions
"""


class GeoSentinelError(Exception):
    """Base exception for all GeoSentinel errors."""
    pass


class SentinelDownloadError(GeoSentinelError):
    """Raised when Sentinel imagery cannot be downloaded."""
    pass


class GeoTIFFError(GeoSentinelError):
    """Raised when GeoTIFF creation or reading fails."""
    pass


class ModelInferenceError(GeoSentinelError):
    """Raised when an AI model fails during inference."""
    pass


class DatabaseError(GeoSentinelError):
    """Raised when database operations fail."""
    pass


class ReportGenerationError(GeoSentinelError):
    """Raised when report generation fails."""
    pass


class OSINTError(GeoSentinelError):
    """Raised when OSINT collection fails."""
    pass


class ValidationError(GeoSentinelError):
    """Raised when AI evidence validation fails."""
    pass