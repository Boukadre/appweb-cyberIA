"""
CyberSec Blue Team Toolkit V2 - Modules Package
Professional modular structure for cybersecurity analysis
"""

__version__ = "2.0.0"
__author__ = "Blue Team Security"

# Module exports
from .ssh_detector import render_ssh_forensics
from .phishing_ai import render_phishing_detector
from .pass_auditor import render_password_auditor
from .payload_ml import render_payload_classifier

__all__ = [
    "render_ssh_forensics",
    "render_phishing_detector",
    "render_password_auditor",
    "render_payload_classifier",
]

