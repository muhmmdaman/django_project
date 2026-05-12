"""Security utilities for the Academic Intelligence System.
Provides functions for input validation, sanitization, and protection.
"""
import bleach
import logging
from html import escape
from django.utils.html import strip_tags
from django.core.exceptions import ValidationError
logger = logging.getLogger("django")
ALLOWED_TAGS = ["b", "i", "u", "strong", "em", "p", "br", "ul", "ol", "li", "a"]
ALLOWED_ATTRIBUTES = {"a": ["href", "title"]}
def sanitize_html(html_input: str, max_length: int = 5000) -> str:
    """Sanitize HTML input to prevent XSS attacks.
    Args:
        html_input: Raw HTML string to sanitize
        max_length: Maximum allowed length (default 5000 chars)
    Returns:
        Sanitized HTML string safe for rendering
    Raises:
        ValidationError: If input exceeds max_length
    """
    if len(html_input) > max_length:
        raise ValidationError(
            f"Input exceeds maximum length of {max_length} characters"
        )
    cleaned = bleach.clean(
        html_input, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True
    )
    return cleaned
def sanitize_text(text_input: str, max_length: int = 5000) -> str:
    """Sanitize plain text input.
    Args:
        text_input: Raw text string to sanitize
        max_length: Maximum allowed length (default 5000 chars)
    Returns:
        Sanitized plain text
    Raises:
        ValidationError: If input exceeds max_length
    """
    if len(text_input) > max_length:
        raise ValidationError(
            f"Input exceeds maximum length of {max_length} characters"
        )
    text = strip_tags(text_input.strip())
    text = escape(text)
    return text
def validate_email(email: str) -> str:
    """Validate and sanitize email addresses.
    Args:
        email: Email address to validate
    Returns:
        Validated email address
    Raises:
        ValidationError: If email is invalid
    """
    from django.core.validators import EmailValidator
    validator = EmailValidator()
    try:
        validator(email)
        return email.lower().strip()
    except ValidationError:
        raise ValidationError("Invalid email address")
def validate_username(username: str) -> str:
    """Validate username format.
    Args:
        username: Username to validate
    Returns:
        Validated username
    Raises:
        ValidationError: If username is invalid
    """
    if not username or len(username) < 3:
        raise ValidationError("Username must be at least 3 characters")
    if len(username) > 30:
        raise ValidationError("Username must not exceed 30 characters")
    if not username.replace("_", "").replace(".", "").isalnum():
        raise ValidationError(
            "Username can only contain letters, numbers, dots, and underscores"
        )
    return username.strip()
def get_client_ip(request) -> str:
    """Get client IP address from request, handling proxy headers.
    Args:
        request: Django HTTP request object
    Returns:
        Client IP address
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
def get_user_agent(request) -> str:
    """Get user agent from request.
    Args:
        request: Django HTTP request object
    Returns:
        User agent string (truncated to 500 chars)
    """
    return request.META.get("HTTP_USER_AGENT", "")[:500]
def log_security_event(
    event_type: str,
    user=None,
    ip_address: str = None,
    details: dict = None,
    level: str = "INFO",
) -> None:
    """Log security-related events for audit trail.
    Args:
        event_type: Type of security event
        user: User involved in event
        ip_address: IP address of request
        details: Additional event details
        level: Log level (INFO, WARNING, ERROR, CRITICAL)
    """
    message = f"SECURITY EVENT: {event_type}"
    if user:
        message += f" | User: {user.username}"
    if ip_address:
        message += f" | IP: {ip_address}"
    if details:
        message += f" | Details: {details}"
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(message)
