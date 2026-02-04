#!/usr/bin/env python3
"""
Secret Scanner - Comprehensive secret detection for source code and configuration files.

Detects API keys, tokens, passwords, private keys, and credentials across 50+ providers.
Features entropy-based detection, smart false positive filtering, and risk scoring.

Usage:
    python detect-secrets.py <path> [options]
    python detect-secrets.py ./src --format json --output findings.json
    python detect-secrets.py . --severity high --no-entropy
"""

import argparse
import hashlib
import json
import math
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class SecretType(Enum):
    # Cloud Providers
    AWS_ACCESS_KEY = "aws_access_key"
    AWS_SECRET_KEY = "aws_secret_key"
    AWS_SESSION_TOKEN = "aws_session_token"
    GCP_API_KEY = "gcp_api_key"
    GCP_SERVICE_ACCOUNT = "gcp_service_account"
    AZURE_STORAGE_KEY = "azure_storage_key"
    AZURE_CONNECTION_STRING = "azure_connection_string"
    AZURE_SAS_TOKEN = "azure_sas_token"

    # Code Platforms
    GITHUB_TOKEN = "github_token"
    GITHUB_OAUTH = "github_oauth"
    GITLAB_TOKEN = "gitlab_token"
    BITBUCKET_TOKEN = "bitbucket_token"
    NPM_TOKEN = "npm_token"
    PYPI_TOKEN = "pypi_token"

    # Payment Services
    STRIPE_SECRET_KEY = "stripe_secret_key"
    STRIPE_RESTRICTED_KEY = "stripe_restricted_key"
    PAYPAL_SECRET = "paypal_secret"
    SQUARE_TOKEN = "square_token"

    # Communication
    TWILIO_ACCOUNT_SID = "twilio_account_sid"
    TWILIO_AUTH_TOKEN = "twilio_auth_token"
    TWILIO_API_KEY = "twilio_api_key"
    SENDGRID_API_KEY = "sendgrid_api_key"
    MAILCHIMP_API_KEY = "mailchimp_api_key"
    SLACK_TOKEN = "slack_token"
    SLACK_WEBHOOK = "slack_webhook"
    DISCORD_TOKEN = "discord_token"
    DISCORD_WEBHOOK = "discord_webhook"

    # Databases
    MONGODB_URI = "mongodb_uri"
    POSTGRES_URI = "postgres_uri"
    MYSQL_URI = "mysql_uri"
    REDIS_URI = "redis_uri"

    # AI Services
    OPENAI_API_KEY = "openai_api_key"
    ANTHROPIC_API_KEY = "anthropic_api_key"

    # Other Services
    FIREBASE_KEY = "firebase_key"
    CLOUDFLARE_API_KEY = "cloudflare_api_key"
    DATADOG_API_KEY = "datadog_api_key"
    NEWRELIC_KEY = "newrelic_key"
    AUTH0_SECRET = "auth0_secret"
    OKTA_TOKEN = "okta_token"
    JWT_SECRET = "jwt_secret"
    PRIVATE_KEY = "private_key"
    GENERIC_API_KEY = "generic_api_key"
    GENERIC_SECRET = "generic_secret"
    GENERIC_PASSWORD = "generic_password"
    GENERIC_TOKEN = "generic_token"
    HIGH_ENTROPY = "high_entropy"
    BASIC_AUTH = "basic_auth"
    BEARER_TOKEN = "bearer_token"
    HEROKU_API_KEY = "heroku_api_key"
    DIGITALOCEAN_TOKEN = "digitalocean_token"


@dataclass
class SecretPattern:
    """Definition of a secret detection pattern."""
    name: str
    secret_type: SecretType
    pattern: str
    severity: Severity
    provider: str
    description: str
    keywords: List[str] = field(default_factory=list)
    false_positive_patterns: List[str] = field(default_factory=list)


@dataclass
class Finding:
    """A detected secret finding."""
    id: str
    file: str
    line: int
    column: int
    secret_type: str
    provider: str
    value_preview: str
    value_hash: str
    confidence: float
    risk_score: int
    severity: str
    context: str
    pattern_name: str
    remediation: List[str]
    verified: bool = False
    entropy: Optional[float] = None


# =============================================================================
# SECRET PATTERNS
# =============================================================================

SECRET_PATTERNS: List[SecretPattern] = [
    # =========================================================================
    # AWS
    # =========================================================================
    SecretPattern(
        name="AWS Access Key ID",
        secret_type=SecretType.AWS_ACCESS_KEY,
        pattern=r'(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}',
        severity=Severity.CRITICAL,
        provider="AWS",
        description="AWS Access Key ID - provides access to AWS services",
        keywords=["aws", "access_key", "aws_access"],
        false_positive_patterns=[r'AKIAIOSFODNN7EXAMPLE', r'EXAMPLE']
    ),
    SecretPattern(
        name="AWS Secret Access Key",
        secret_type=SecretType.AWS_SECRET_KEY,
        pattern=r'(?i)(?:aws)?[_\-\.]?(?:secret)?[_\-\.]?(?:access)?[_\-\.]?key[\'"\s]*[:=]\s*[\'"][A-Za-z0-9/+=]{40}[\'"]',
        severity=Severity.CRITICAL,
        provider="AWS",
        description="AWS Secret Access Key - full access to AWS account",
        keywords=["aws_secret", "secret_key", "secret_access"]
    ),
    SecretPattern(
        name="AWS Session Token",
        secret_type=SecretType.AWS_SESSION_TOKEN,
        pattern=r'(?i)(?:aws)?[_\-\.]?session[_\-\.]?token[\'"\s]*[:=]\s*[\'"][A-Za-z0-9/+=]{100,}[\'"]',
        severity=Severity.HIGH,
        provider="AWS",
        description="AWS Session Token - temporary credentials",
        keywords=["session_token", "aws_session"]
    ),

    # =========================================================================
    # GCP
    # =========================================================================
    SecretPattern(
        name="GCP API Key",
        secret_type=SecretType.GCP_API_KEY,
        pattern=r'AIza[0-9A-Za-z_-]{35}',
        severity=Severity.HIGH,
        provider="GCP",
        description="Google Cloud Platform API Key",
        keywords=["gcp", "google", "api_key"]
    ),
    SecretPattern(
        name="GCP Service Account",
        secret_type=SecretType.GCP_SERVICE_ACCOUNT,
        pattern=r'(?i)"type"\s*:\s*"service_account"',
        severity=Severity.CRITICAL,
        provider="GCP",
        description="GCP Service Account JSON key file",
        keywords=["service_account", "gcp", "google"]
    ),

    # =========================================================================
    # Azure
    # =========================================================================
    SecretPattern(
        name="Azure Storage Key",
        secret_type=SecretType.AZURE_STORAGE_KEY,
        pattern=r'(?i)(?:DefaultEndpointsProtocol|AccountKey)\s*=\s*[A-Za-z0-9+/=]{86,88}',
        severity=Severity.CRITICAL,
        provider="Azure",
        description="Azure Storage Account Key",
        keywords=["azure", "storage", "account_key"]
    ),
    SecretPattern(
        name="Azure Connection String",
        secret_type=SecretType.AZURE_CONNECTION_STRING,
        pattern=r'(?i)(?:Server|Data\s+Source)=[^;]+;(?:Database|Initial\s+Catalog)=[^;]+;(?:User\s+Id|UID)=[^;]+;(?:Password|PWD)=[^;]+',
        severity=Severity.CRITICAL,
        provider="Azure",
        description="Azure SQL Connection String with credentials",
        keywords=["azure", "connection_string", "sql"]
    ),
    SecretPattern(
        name="Azure SAS Token",
        secret_type=SecretType.AZURE_SAS_TOKEN,
        pattern=r'(?i)[?&]sig=[A-Za-z0-9%+/=]{43,}',
        severity=Severity.HIGH,
        provider="Azure",
        description="Azure Shared Access Signature Token",
        keywords=["azure", "sas", "signature"]
    ),

    # =========================================================================
    # GitHub
    # =========================================================================
    SecretPattern(
        name="GitHub Personal Access Token",
        secret_type=SecretType.GITHUB_TOKEN,
        pattern=r'ghp_[A-Za-z0-9_]{36,255}',
        severity=Severity.CRITICAL,
        provider="GitHub",
        description="GitHub Personal Access Token",
        keywords=["github", "token", "pat"]
    ),
    SecretPattern(
        name="GitHub OAuth Token",
        secret_type=SecretType.GITHUB_OAUTH,
        pattern=r'gho_[A-Za-z0-9_]{36,255}',
        severity=Severity.CRITICAL,
        provider="GitHub",
        description="GitHub OAuth Access Token",
        keywords=["github", "oauth"]
    ),
    SecretPattern(
        name="GitHub App Token",
        secret_type=SecretType.GITHUB_TOKEN,
        pattern=r'(?:ghu|ghs|ghr)_[A-Za-z0-9_]{36,255}',
        severity=Severity.CRITICAL,
        provider="GitHub",
        description="GitHub App Token (User, Server, Refresh)",
        keywords=["github", "app", "token"]
    ),
    SecretPattern(
        name="GitHub Fine-grained Token",
        secret_type=SecretType.GITHUB_TOKEN,
        pattern=r'github_pat_[A-Za-z0-9_]{22,255}',
        severity=Severity.CRITICAL,
        provider="GitHub",
        description="GitHub Fine-grained Personal Access Token",
        keywords=["github", "token", "fine_grained"]
    ),

    # =========================================================================
    # GitLab
    # =========================================================================
    SecretPattern(
        name="GitLab Personal Access Token",
        secret_type=SecretType.GITLAB_TOKEN,
        pattern=r'glpat-[A-Za-z0-9_-]{20,}',
        severity=Severity.CRITICAL,
        provider="GitLab",
        description="GitLab Personal Access Token",
        keywords=["gitlab", "token", "pat"]
    ),
    SecretPattern(
        name="GitLab Pipeline Token",
        secret_type=SecretType.GITLAB_TOKEN,
        pattern=r'glptt-[A-Za-z0-9_-]{20,}',
        severity=Severity.HIGH,
        provider="GitLab",
        description="GitLab Pipeline Trigger Token",
        keywords=["gitlab", "pipeline", "trigger"]
    ),
    SecretPattern(
        name="GitLab Runner Token",
        secret_type=SecretType.GITLAB_TOKEN,
        pattern=r'GR1348941[A-Za-z0-9_-]{20,}',
        severity=Severity.HIGH,
        provider="GitLab",
        description="GitLab Runner Registration Token",
        keywords=["gitlab", "runner"]
    ),

    # =========================================================================
    # npm / PyPI
    # =========================================================================
    SecretPattern(
        name="npm Access Token",
        secret_type=SecretType.NPM_TOKEN,
        pattern=r'npm_[A-Za-z0-9]{36}',
        severity=Severity.CRITICAL,
        provider="npm",
        description="npm Access Token for publishing packages",
        keywords=["npm", "token", "publish"]
    ),
    SecretPattern(
        name="PyPI API Token",
        secret_type=SecretType.PYPI_TOKEN,
        pattern=r'pypi-AgEIcHlwaS5vcmc[A-Za-z0-9_-]{50,}',
        severity=Severity.CRITICAL,
        provider="PyPI",
        description="PyPI API Token for publishing packages",
        keywords=["pypi", "token", "publish"]
    ),

    # =========================================================================
    # Stripe
    # =========================================================================
    SecretPattern(
        name="Stripe Secret Key",
        secret_type=SecretType.STRIPE_SECRET_KEY,
        pattern=r'sk_live_[A-Za-z0-9]{24,}',
        severity=Severity.CRITICAL,
        provider="Stripe",
        description="Stripe Live Secret Key - full API access",
        keywords=["stripe", "secret", "live"]
    ),
    SecretPattern(
        name="Stripe Test Secret Key",
        secret_type=SecretType.STRIPE_SECRET_KEY,
        pattern=r'sk_test_[A-Za-z0-9]{24,}',
        severity=Severity.MEDIUM,
        provider="Stripe",
        description="Stripe Test Secret Key",
        keywords=["stripe", "secret", "test"],
        false_positive_patterns=[r'sk_test_[xX]{24}', r'sk_test_EXAMPLE']
    ),
    SecretPattern(
        name="Stripe Restricted Key",
        secret_type=SecretType.STRIPE_RESTRICTED_KEY,
        pattern=r'rk_live_[A-Za-z0-9]{24,}',
        severity=Severity.HIGH,
        provider="Stripe",
        description="Stripe Live Restricted Key",
        keywords=["stripe", "restricted", "live"]
    ),

    # =========================================================================
    # Twilio
    # =========================================================================
    SecretPattern(
        name="Twilio Account SID",
        secret_type=SecretType.TWILIO_ACCOUNT_SID,
        pattern=r'AC[a-f0-9]{32}',
        severity=Severity.MEDIUM,
        provider="Twilio",
        description="Twilio Account SID",
        keywords=["twilio", "account", "sid"]
    ),
    SecretPattern(
        name="Twilio Auth Token",
        secret_type=SecretType.TWILIO_AUTH_TOKEN,
        pattern=r'(?i)twilio[_\-\.]?(?:auth)?[_\-\.]?token[\'"\s]*[:=]\s*[\'"][a-f0-9]{32}[\'"]',
        severity=Severity.CRITICAL,
        provider="Twilio",
        description="Twilio Auth Token",
        keywords=["twilio", "auth", "token"]
    ),
    SecretPattern(
        name="Twilio API Key",
        secret_type=SecretType.TWILIO_API_KEY,
        pattern=r'SK[a-f0-9]{32}',
        severity=Severity.HIGH,
        provider="Twilio",
        description="Twilio API Key",
        keywords=["twilio", "api", "key"]
    ),

    # =========================================================================
    # SendGrid
    # =========================================================================
    SecretPattern(
        name="SendGrid API Key",
        secret_type=SecretType.SENDGRID_API_KEY,
        pattern=r'SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}',
        severity=Severity.CRITICAL,
        provider="SendGrid",
        description="SendGrid API Key",
        keywords=["sendgrid", "api", "key"]
    ),

    # =========================================================================
    # Slack
    # =========================================================================
    SecretPattern(
        name="Slack Bot Token",
        secret_type=SecretType.SLACK_TOKEN,
        pattern=r'xoxb-[0-9]{10,13}-[0-9]{10,13}-[A-Za-z0-9]{24}',
        severity=Severity.CRITICAL,
        provider="Slack",
        description="Slack Bot Token",
        keywords=["slack", "bot", "token"],
        false_positive_patterns=[r'xoxb-PLACEHOLDER-EXAMPLE']
    ),
    SecretPattern(
        name="Slack User Token",
        secret_type=SecretType.SLACK_TOKEN,
        pattern=r'xoxp-[0-9]{10,13}-[0-9]{10,13}-[0-9]{10,13}-[a-f0-9]{32}',
        severity=Severity.CRITICAL,
        provider="Slack",
        description="Slack User Token",
        keywords=["slack", "user", "token"]
    ),
    SecretPattern(
        name="Slack Webhook URL",
        secret_type=SecretType.SLACK_WEBHOOK,
        pattern=r'https://hooks\.slack\.com/services/T[A-Z0-9]{8,}/B[A-Z0-9]{8,}/[A-Za-z0-9]{24}',
        severity=Severity.HIGH,
        provider="Slack",
        description="Slack Incoming Webhook URL",
        keywords=["slack", "webhook"]
    ),

    # =========================================================================
    # Discord
    # =========================================================================
    SecretPattern(
        name="Discord Bot Token",
        secret_type=SecretType.DISCORD_TOKEN,
        pattern=r'[MN][A-Za-z\d]{23,}\.[\w-]{6}\.[\w-]{27}',
        severity=Severity.CRITICAL,
        provider="Discord",
        description="Discord Bot Token",
        keywords=["discord", "bot", "token"]
    ),
    SecretPattern(
        name="Discord Webhook URL",
        secret_type=SecretType.DISCORD_WEBHOOK,
        pattern=r'https://discord(?:app)?\.com/api/webhooks/\d+/[A-Za-z0-9_-]+',
        severity=Severity.HIGH,
        provider="Discord",
        description="Discord Webhook URL",
        keywords=["discord", "webhook"]
    ),

    # =========================================================================
    # Databases
    # =========================================================================
    SecretPattern(
        name="MongoDB Connection String",
        secret_type=SecretType.MONGODB_URI,
        pattern=r'mongodb(?:\+srv)?://[^:]+:[^@]+@[^/]+',
        severity=Severity.CRITICAL,
        provider="MongoDB",
        description="MongoDB Connection String with credentials",
        keywords=["mongodb", "connection", "uri"]
    ),
    SecretPattern(
        name="PostgreSQL Connection String",
        secret_type=SecretType.POSTGRES_URI,
        pattern=r'postgres(?:ql)?://[^:]+:[^@]+@[^/]+',
        severity=Severity.CRITICAL,
        provider="PostgreSQL",
        description="PostgreSQL Connection String with credentials",
        keywords=["postgres", "connection", "uri"]
    ),
    SecretPattern(
        name="MySQL Connection String",
        secret_type=SecretType.MYSQL_URI,
        pattern=r'mysql://[^:]+:[^@]+@[^/]+',
        severity=Severity.CRITICAL,
        provider="MySQL",
        description="MySQL Connection String with credentials",
        keywords=["mysql", "connection", "uri"]
    ),
    SecretPattern(
        name="Redis Connection String",
        secret_type=SecretType.REDIS_URI,
        pattern=r'redis://[^:]*:[^@]+@[^/]+',
        severity=Severity.HIGH,
        provider="Redis",
        description="Redis Connection String with password",
        keywords=["redis", "connection", "uri"]
    ),

    # =========================================================================
    # AI Services
    # =========================================================================
    SecretPattern(
        name="OpenAI API Key",
        secret_type=SecretType.OPENAI_API_KEY,
        pattern=r'sk-[A-Za-z0-9]{20}T3BlbkFJ[A-Za-z0-9]{20}',
        severity=Severity.CRITICAL,
        provider="OpenAI",
        description="OpenAI API Key",
        keywords=["openai", "api", "key", "gpt"]
    ),
    SecretPattern(
        name="OpenAI API Key (Project)",
        secret_type=SecretType.OPENAI_API_KEY,
        pattern=r'sk-proj-[A-Za-z0-9_-]{48,}',
        severity=Severity.CRITICAL,
        provider="OpenAI",
        description="OpenAI Project API Key",
        keywords=["openai", "api", "key", "project"]
    ),
    SecretPattern(
        name="Anthropic API Key",
        secret_type=SecretType.ANTHROPIC_API_KEY,
        pattern=r'sk-ant-api[0-9]{2}-[A-Za-z0-9_-]{93}',
        severity=Severity.CRITICAL,
        provider="Anthropic",
        description="Anthropic API Key",
        keywords=["anthropic", "claude", "api", "key"]
    ),

    # =========================================================================
    # Other Services
    # =========================================================================
    SecretPattern(
        name="Firebase API Key",
        secret_type=SecretType.FIREBASE_KEY,
        pattern=r'(?i)firebase[_\-\.]?(?:api)?[_\-\.]?key[\'"\s]*[:=]\s*[\'"][A-Za-z0-9_-]{39}[\'"]',
        severity=Severity.HIGH,
        provider="Firebase",
        description="Firebase API Key",
        keywords=["firebase", "api", "key"]
    ),
    SecretPattern(
        name="Cloudflare API Key",
        secret_type=SecretType.CLOUDFLARE_API_KEY,
        pattern=r'(?i)cloudflare[_\-\.]?(?:api)?[_\-\.]?key[\'"\s]*[:=]\s*[\'"][A-Za-z0-9]{37}[\'"]',
        severity=Severity.CRITICAL,
        provider="Cloudflare",
        description="Cloudflare API Key",
        keywords=["cloudflare", "api", "key"]
    ),
    SecretPattern(
        name="Heroku API Key",
        secret_type=SecretType.HEROKU_API_KEY,
        pattern=r'(?i)heroku[_\-\.]?(?:api)?[_\-\.]?key[\'"\s]*[:=]\s*[\'"][0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}[\'"]',
        severity=Severity.CRITICAL,
        provider="Heroku",
        description="Heroku API Key",
        keywords=["heroku", "api", "key"]
    ),
    SecretPattern(
        name="DigitalOcean Token",
        secret_type=SecretType.DIGITALOCEAN_TOKEN,
        pattern=r'dop_v1_[a-f0-9]{64}',
        severity=Severity.CRITICAL,
        provider="DigitalOcean",
        description="DigitalOcean Personal Access Token",
        keywords=["digitalocean", "token"]
    ),
    SecretPattern(
        name="Datadog API Key",
        secret_type=SecretType.DATADOG_API_KEY,
        pattern=r'(?i)datadog[_\-\.]?(?:api)?[_\-\.]?key[\'"\s]*[:=]\s*[\'"][a-f0-9]{32}[\'"]',
        severity=Severity.HIGH,
        provider="Datadog",
        description="Datadog API Key",
        keywords=["datadog", "api", "key"]
    ),
    SecretPattern(
        name="New Relic License Key",
        secret_type=SecretType.NEWRELIC_KEY,
        pattern=r'(?i)new[_\-\.]?relic[_\-\.]?(?:license)?[_\-\.]?key[\'"\s]*[:=]\s*[\'"][A-Za-z0-9]{40}[\'"]',
        severity=Severity.HIGH,
        provider="New Relic",
        description="New Relic License Key",
        keywords=["newrelic", "license", "key"]
    ),
    SecretPattern(
        name="Mailchimp API Key",
        secret_type=SecretType.MAILCHIMP_API_KEY,
        pattern=r'[a-f0-9]{32}-us[0-9]{1,2}',
        severity=Severity.HIGH,
        provider="Mailchimp",
        description="Mailchimp API Key",
        keywords=["mailchimp", "api", "key"]
    ),

    # =========================================================================
    # Private Keys
    # =========================================================================
    SecretPattern(
        name="RSA Private Key",
        secret_type=SecretType.PRIVATE_KEY,
        pattern=r'-----BEGIN RSA PRIVATE KEY-----',
        severity=Severity.CRITICAL,
        provider="Cryptographic",
        description="RSA Private Key",
        keywords=["rsa", "private", "key"]
    ),
    SecretPattern(
        name="OpenSSH Private Key",
        secret_type=SecretType.PRIVATE_KEY,
        pattern=r'-----BEGIN OPENSSH PRIVATE KEY-----',
        severity=Severity.CRITICAL,
        provider="Cryptographic",
        description="OpenSSH Private Key",
        keywords=["ssh", "private", "key"]
    ),
    SecretPattern(
        name="EC Private Key",
        secret_type=SecretType.PRIVATE_KEY,
        pattern=r'-----BEGIN EC PRIVATE KEY-----',
        severity=Severity.CRITICAL,
        provider="Cryptographic",
        description="Elliptic Curve Private Key",
        keywords=["ec", "private", "key"]
    ),
    SecretPattern(
        name="PGP Private Key",
        secret_type=SecretType.PRIVATE_KEY,
        pattern=r'-----BEGIN PGP PRIVATE KEY BLOCK-----',
        severity=Severity.CRITICAL,
        provider="Cryptographic",
        description="PGP Private Key Block",
        keywords=["pgp", "private", "key"]
    ),
    SecretPattern(
        name="DSA Private Key",
        secret_type=SecretType.PRIVATE_KEY,
        pattern=r'-----BEGIN DSA PRIVATE KEY-----',
        severity=Severity.CRITICAL,
        provider="Cryptographic",
        description="DSA Private Key",
        keywords=["dsa", "private", "key"]
    ),

    # =========================================================================
    # Generic Patterns
    # =========================================================================
    SecretPattern(
        name="Generic API Key",
        secret_type=SecretType.GENERIC_API_KEY,
        pattern=r'(?i)(?:api[_\-\.]?key|apikey)[\'"\s]*[:=]\s*[\'"][A-Za-z0-9_\-]{20,}[\'"]',
        severity=Severity.MEDIUM,
        provider="Generic",
        description="Generic API Key pattern",
        keywords=["api", "key"]
    ),
    SecretPattern(
        name="Generic Secret",
        secret_type=SecretType.GENERIC_SECRET,
        pattern=r'(?i)(?:secret|client[_\-\.]?secret)[\'"\s]*[:=]\s*[\'"][A-Za-z0-9_\-]{20,}[\'"]',
        severity=Severity.MEDIUM,
        provider="Generic",
        description="Generic Secret pattern",
        keywords=["secret", "client_secret"]
    ),
    SecretPattern(
        name="Generic Password",
        secret_type=SecretType.GENERIC_PASSWORD,
        pattern=r'(?i)(?:password|passwd|pwd)[\'"\s]*[:=]\s*[\'"][^\'"]{8,}[\'"]',
        severity=Severity.HIGH,
        provider="Generic",
        description="Hardcoded password",
        keywords=["password", "passwd", "pwd"]
    ),
    SecretPattern(
        name="Generic Token",
        secret_type=SecretType.GENERIC_TOKEN,
        pattern=r'(?i)(?:token|bearer|auth[_\-\.]?token)[\'"\s]*[:=]\s*[\'"][A-Za-z0-9_\-\.]{20,}[\'"]',
        severity=Severity.MEDIUM,
        provider="Generic",
        description="Generic Token pattern",
        keywords=["token", "bearer", "auth"]
    ),
    SecretPattern(
        name="Basic Auth Header",
        secret_type=SecretType.BASIC_AUTH,
        pattern=r'(?i)authorization[\'"\s]*[:=]\s*[\'"]Basic\s+[A-Za-z0-9+/=]{20,}[\'"]',
        severity=Severity.HIGH,
        provider="HTTP",
        description="HTTP Basic Authentication header",
        keywords=["authorization", "basic"]
    ),
    SecretPattern(
        name="Bearer Token Header",
        secret_type=SecretType.BEARER_TOKEN,
        pattern=r'(?i)authorization[\'"\s]*[:=]\s*[\'"]Bearer\s+[A-Za-z0-9_\-\.]{20,}[\'"]',
        severity=Severity.HIGH,
        provider="HTTP",
        description="HTTP Bearer Token header",
        keywords=["authorization", "bearer"]
    ),
    SecretPattern(
        name="JWT Token",
        secret_type=SecretType.JWT_SECRET,
        pattern=r'eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}',
        severity=Severity.MEDIUM,
        provider="JWT",
        description="JSON Web Token",
        keywords=["jwt", "token"]
    ),
]


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def calculate_entropy(string: str) -> float:
    """Calculate Shannon entropy of a string."""
    if not string:
        return 0.0

    counts = Counter(string)
    length = len(string)

    entropy = -sum(
        (count / length) * math.log2(count / length)
        for count in counts.values()
    )

    return round(entropy, 2)


def mask_secret(value: str, show_chars: int = 4) -> str:
    """Mask a secret value, showing only first and last few characters."""
    if len(value) <= show_chars * 2:
        return "*" * len(value)
    return f"{value[:show_chars]}...{value[-show_chars:]}"


def hash_value(value: str) -> str:
    """Generate SHA256 hash of a value."""
    return f"sha256:{hashlib.sha256(value.encode()).hexdigest()[:16]}"


def generate_finding_id() -> str:
    """Generate a unique finding ID."""
    timestamp = datetime.now().strftime("%Y%m%d")
    import random
    return f"S-{timestamp}-{random.randint(1000, 9999)}"


def get_context(lines: List[str], line_num: int, context_lines: int = 2) -> str:
    """Get surrounding context for a finding."""
    start = max(0, line_num - context_lines - 1)
    end = min(len(lines), line_num + context_lines)

    context_parts = []
    for i in range(start, end):
        prefix = ">>>" if i == line_num - 1 else "   "
        context_parts.append(f"{prefix} {i + 1}: {lines[i].rstrip()}")

    return "\n".join(context_parts)


def calculate_risk_score(
    severity: Severity,
    file_path: str,
    confidence: float,
    in_git_history: bool = False
) -> int:
    """Calculate risk score based on multiple factors."""

    # Base sensitivity score by severity
    sensitivity_scores = {
        Severity.CRITICAL: 100,
        Severity.HIGH: 80,
        Severity.MEDIUM: 60,
        Severity.LOW: 40,
        Severity.INFO: 20,
    }
    sensitivity = sensitivity_scores.get(severity, 50)

    # Exposure score based on file location
    exposure = 50  # Default
    path_lower = file_path.lower()

    if any(x in path_lower for x in ['.env', 'secrets', 'credentials', 'config']):
        exposure = 80
    elif any(x in path_lower for x in ['test', 'spec', 'mock', 'example', 'sample']):
        exposure = 30
    elif any(x in path_lower for x in ['production', 'prod', 'live']):
        exposure = 95

    if in_git_history:
        exposure = min(exposure + 20, 100)

    # Verifiability based on confidence
    verifiability = int(confidence * 100)

    # Scope (placeholder - could be enhanced with more context)
    scope = 60

    # Calculate weighted score
    risk_score = int(
        (sensitivity * 0.40) +
        (exposure * 0.30) +
        (verifiability * 0.15) +
        (scope * 0.15)
    )

    return min(100, max(0, risk_score))


def get_remediation_steps(secret_type: SecretType, provider: str) -> List[str]:
    """Get remediation steps for a secret type."""

    base_steps = [
        "1. Immediately revoke/rotate the exposed credential",
        "2. Remove the secret from source code",
        "3. Use environment variables or a secrets manager",
        "4. Update .gitignore to prevent future commits",
        "5. If committed to git, clean history with BFG or git filter-branch",
    ]

    provider_specific = {
        "AWS": [
            "AWS Console: IAM > Users > Security Credentials > Deactivate/Delete",
            "Create new access key and update applications",
            "Review CloudTrail logs for unauthorized access",
            "Consider using IAM roles instead of access keys",
        ],
        "GitHub": [
            "GitHub: Settings > Developer settings > Personal access tokens > Revoke",
            "Generate new token with minimal required scopes",
            "Review repository access and audit logs",
        ],
        "Stripe": [
            "Stripe Dashboard: Developers > API keys > Roll key",
            "Update all applications using this key",
            "Review Stripe logs for suspicious activity",
        ],
        "Slack": [
            "Slack: App settings > OAuth & Permissions > Regenerate token",
            "Review bot activity and workspace access logs",
        ],
        "OpenAI": [
            "OpenAI: API keys > Delete and create new key",
            "Review usage logs for unexpected API calls",
            "Set up usage limits and alerts",
        ],
    }

    steps = base_steps.copy()
    if provider in provider_specific:
        steps.extend(["\nProvider-specific steps:"] + provider_specific[provider])

    return steps


# =============================================================================
# FILE FILTERING
# =============================================================================

# File extensions to scan
SCANNABLE_EXTENSIONS = {
    # Source code
    '.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.go', '.rb', '.php',
    '.cs', '.swift', '.kt', '.rs', '.c', '.cpp', '.h', '.hpp', '.scala',
    # Config files
    '.env', '.json', '.yaml', '.yml', '.xml', '.toml', '.ini', '.conf',
    '.cfg', '.properties', '.config',
    # Infrastructure
    '.tf', '.tfvars', '.hcl', '.dockerfile',
    # Shell
    '.sh', '.bash', '.zsh', '.ps1', '.bat', '.cmd',
    # Other
    '.sql', '.graphql', '.prisma', '.txt', '.md', '.rst',
}

# Files to always scan regardless of extension
ALWAYS_SCAN_FILES = {
    '.env', '.env.local', '.env.development', '.env.production', '.env.test',
    'dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
    '.npmrc', '.pypirc', '.netrc', '.pgpass', '.my.cnf',
    'credentials', 'secrets', 'config', 'settings',
}

# Directories to skip
SKIP_DIRECTORIES = {
    '.git', '.svn', '.hg', 'node_modules', '__pycache__', '.pytest_cache',
    'venv', '.venv', 'env', '.env', 'virtualenv', '.tox',
    'dist', 'build', 'target', 'out', 'bin', 'obj',
    '.idea', '.vscode', '.eclipse', '.settings',
    'vendor', 'bower_components', 'packages',
    '.terraform', '.serverless',
    'coverage', '.nyc_output', 'htmlcov',
}

# Files to skip (exact match or pattern)
SKIP_FILES = {
    'package-lock.json', 'yarn.lock', 'poetry.lock', 'Pipfile.lock',
    'composer.lock', 'Gemfile.lock', 'Cargo.lock', 'go.sum',
    '.DS_Store', 'Thumbs.db',
}


def should_scan_file(file_path: Path) -> bool:
    """Determine if a file should be scanned."""
    # Check if in skip directory
    for part in file_path.parts:
        if part in SKIP_DIRECTORIES:
            return False

    # Check if file should be skipped
    if file_path.name in SKIP_FILES:
        return False

    # Check if always scan
    if file_path.name.lower() in ALWAYS_SCAN_FILES:
        return True

    # Check extension
    if file_path.suffix.lower() in SCANNABLE_EXTENSIONS:
        return True

    # Check for files without extension that might contain secrets
    if not file_path.suffix and file_path.name.lower() in ALWAYS_SCAN_FILES:
        return True

    return False


def is_test_file(file_path: str) -> bool:
    """Check if file is a test/example file."""
    path_lower = file_path.lower()
    test_indicators = [
        'test', '_test', 'test_', '.test.', '_spec', '.spec.',
        'mock', 'fake', 'dummy', 'example', 'sample', 'demo',
        'fixture', '__tests__', 'tests/', 'spec/',
    ]
    return any(indicator in path_lower for indicator in test_indicators)


# =============================================================================
# SCANNER CLASS
# =============================================================================

class SecretScanner:
    """Main secret scanner class."""

    def __init__(
        self,
        entropy_threshold: float = 4.5,
        enable_entropy: bool = True,
        min_severity: Severity = Severity.INFO,
        allowlist_patterns: List[str] = None,
    ):
        self.entropy_threshold = entropy_threshold
        self.enable_entropy = enable_entropy
        self.min_severity = min_severity
        self.allowlist_patterns = allowlist_patterns or []
        self.findings: List[Finding] = []
        self.scanned_files = 0
        self.scanned_lines = 0

        # Compile patterns
        self.compiled_patterns = []
        for pattern in SECRET_PATTERNS:
            try:
                compiled = re.compile(pattern.pattern)
                self.compiled_patterns.append((pattern, compiled))
            except re.error as e:
                print(f"Warning: Invalid pattern for {pattern.name}: {e}", file=sys.stderr)

        # Compile false positive patterns
        self.false_positive_regexes = []
        for pattern in SECRET_PATTERNS:
            for fp in pattern.false_positive_patterns:
                try:
                    self.false_positive_regexes.append(re.compile(fp))
                except re.error:
                    pass

        # Compile allowlist patterns
        self.allowlist_regexes = []
        for pattern in self.allowlist_patterns:
            try:
                self.allowlist_regexes.append(re.compile(pattern))
            except re.error:
                pass

    def is_false_positive(self, value: str, file_path: str) -> bool:
        """Check if a value is a known false positive."""
        # Check against false positive patterns
        for regex in self.false_positive_regexes:
            if regex.search(value):
                return True

        # Check against allowlist
        for regex in self.allowlist_regexes:
            if regex.search(value):
                return True

        # Common false positives
        false_positives = [
            'EXAMPLE', 'example', 'YOUR_', 'your_', 'REPLACE', 'replace',
            'INSERT', 'insert', 'PLACEHOLDER', 'placeholder', 'TODO', 'todo',
            'XXXX', 'xxxx', '****', '0000000000', '1234567890',
            'test_api_key', 'fake_', 'mock_', 'dummy_',
        ]

        for fp in false_positives:
            if fp in value:
                return True

        return False

    def scan_line(
        self,
        line: str,
        line_num: int,
        file_path: str,
        all_lines: List[str]
    ) -> List[Finding]:
        """Scan a single line for secrets."""
        findings = []

        for pattern, compiled in self.compiled_patterns:
            # Check severity threshold
            severity_order = [Severity.INFO, Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]
            if severity_order.index(pattern.severity) < severity_order.index(self.min_severity):
                continue

            for match in compiled.finditer(line):
                value = match.group(0)

                # Skip false positives
                if self.is_false_positive(value, file_path):
                    continue

                # Calculate confidence
                confidence = 0.95  # Base confidence for pattern match
                if is_test_file(file_path):
                    confidence *= 0.5

                # Create finding
                finding = Finding(
                    id=generate_finding_id(),
                    file=file_path,
                    line=line_num,
                    column=match.start() + 1,
                    secret_type=pattern.secret_type.value,
                    provider=pattern.provider,
                    value_preview=mask_secret(value),
                    value_hash=hash_value(value),
                    confidence=round(confidence, 2),
                    risk_score=calculate_risk_score(pattern.severity, file_path, confidence),
                    severity=pattern.severity.value,
                    context=get_context(all_lines, line_num),
                    pattern_name=pattern.name,
                    remediation=get_remediation_steps(pattern.secret_type, pattern.provider),
                )
                findings.append(finding)

        return findings

    def scan_for_high_entropy(
        self,
        line: str,
        line_num: int,
        file_path: str,
        all_lines: List[str]
    ) -> List[Finding]:
        """Scan for high-entropy strings that might be secrets."""
        if not self.enable_entropy:
            return []

        findings = []

        # Extract potential secret values
        # Look for quoted strings and values after = or :
        patterns = [
            r'[\'"]([A-Za-z0-9+/=_\-]{20,})[\'"]',  # Quoted strings
            r'=\s*([A-Za-z0-9+/=_\-]{20,})\s*$',    # After equals
            r':\s*([A-Za-z0-9+/=_\-]{20,})\s*$',    # After colon
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, line):
                value = match.group(1)

                # Skip if already found by pattern matching
                if any(f.value_hash == hash_value(value) for f in self.findings):
                    continue

                # Skip false positives
                if self.is_false_positive(value, file_path):
                    continue

                # Calculate entropy
                entropy = calculate_entropy(value)
                if entropy < self.entropy_threshold:
                    continue

                # Check for mixed character classes (more likely to be a secret)
                has_upper = any(c.isupper() for c in value)
                has_lower = any(c.islower() for c in value)
                has_digit = any(c.isdigit() for c in value)
                char_classes = sum([has_upper, has_lower, has_digit])

                if char_classes < 2:
                    continue

                # Check context for secret-related keywords
                context_keywords = ['key', 'secret', 'token', 'password', 'auth', 'credential', 'api']
                line_lower = line.lower()
                keyword_match = any(kw in line_lower for kw in context_keywords)

                confidence = 0.6
                if keyword_match:
                    confidence = 0.8

                # Create finding
                finding = Finding(
                    id=generate_finding_id(),
                    file=file_path,
                    line=line_num,
                    column=match.start() + 1,
                    secret_type=SecretType.HIGH_ENTROPY.value,
                    provider="Unknown",
                    value_preview=mask_secret(value),
                    value_hash=hash_value(value),
                    confidence=round(confidence, 2),
                    risk_score=calculate_risk_score(Severity.LOW, file_path, confidence),
                    severity=Severity.LOW.value,
                    context=get_context(all_lines, line_num),
                    pattern_name="High Entropy String",
                    remediation=get_remediation_steps(SecretType.HIGH_ENTROPY, "Unknown"),
                    entropy=entropy,
                )
                findings.append(finding)

        return findings

    def scan_file(self, file_path: Path) -> List[Finding]:
        """Scan a single file for secrets."""
        findings = []

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)
            return findings

        lines = content.splitlines()
        self.scanned_lines += len(lines)

        for line_num, line in enumerate(lines, start=1):
            # Pattern-based detection
            findings.extend(self.scan_line(line, line_num, str(file_path), lines))

            # Entropy-based detection
            findings.extend(self.scan_for_high_entropy(line, line_num, str(file_path), lines))

        return findings

    def scan_path(self, path: str) -> List[Finding]:
        """Scan a path (file or directory) for secrets."""
        target = Path(path)

        if not target.exists():
            print(f"Error: Path does not exist: {path}", file=sys.stderr)
            return []

        if target.is_file():
            self.scanned_files = 1
            return self.scan_file(target)

        # Scan directory
        for file_path in target.rglob('*'):
            if file_path.is_file() and should_scan_file(file_path):
                self.scanned_files += 1
                findings = self.scan_file(file_path)
                self.findings.extend(findings)

        return self.findings

    def get_summary(self) -> Dict:
        """Get scan summary statistics."""
        severity_counts = {}
        provider_counts = {}
        type_counts = {}

        for finding in self.findings:
            severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1
            provider_counts[finding.provider] = provider_counts.get(finding.provider, 0) + 1
            type_counts[finding.secret_type] = type_counts.get(finding.secret_type, 0) + 1

        return {
            "total_findings": len(self.findings),
            "files_scanned": self.scanned_files,
            "lines_scanned": self.scanned_lines,
            "by_severity": severity_counts,
            "by_provider": provider_counts,
            "by_type": type_counts,
        }


# =============================================================================
# OUTPUT FORMATTERS
# =============================================================================

def format_json(findings: List[Finding], summary: Dict) -> str:
    """Format findings as JSON."""
    output = {
        "scan_timestamp": datetime.now().isoformat(),
        "summary": summary,
        "findings": [asdict(f) for f in findings],
    }
    return json.dumps(output, indent=2)


def format_markdown(findings: List[Finding], summary: Dict) -> str:
    """Format findings as Markdown report."""
    lines = [
        "# Secret Scanner Report",
        "",
        f"**Scan Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Summary",
        "",
        f"- **Total Findings:** {summary['total_findings']}",
        f"- **Files Scanned:** {summary['files_scanned']}",
        f"- **Lines Scanned:** {summary['lines_scanned']}",
        "",
        "### By Severity",
        "",
    ]

    severity_order = ['critical', 'high', 'medium', 'low', 'info']
    for sev in severity_order:
        count = summary['by_severity'].get(sev, 0)
        if count > 0:
            emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢', 'info': '⚪'}.get(sev, '')
            lines.append(f"- {emoji} **{sev.upper()}:** {count}")

    if summary['by_provider']:
        lines.extend([
            "",
            "### By Provider",
            "",
        ])
        for provider, count in sorted(summary['by_provider'].items(), key=lambda x: -x[1]):
            lines.append(f"- **{provider}:** {count}")

    lines.extend([
        "",
        "---",
        "",
        "## Findings",
        "",
    ])

    # Group by severity
    for sev in severity_order:
        sev_findings = [f for f in findings if f.severity == sev]
        if not sev_findings:
            continue

        lines.extend([
            f"### {sev.upper()} ({len(sev_findings)})",
            "",
        ])

        for finding in sev_findings:
            lines.extend([
                f"#### {finding.id}: {finding.pattern_name}",
                "",
                f"- **File:** `{finding.file}`",
                f"- **Line:** {finding.line}",
                f"- **Provider:** {finding.provider}",
                f"- **Confidence:** {finding.confidence}",
                f"- **Risk Score:** {finding.risk_score}",
                f"- **Value:** `{finding.value_preview}`",
                "",
                "**Context:**",
                "```",
                finding.context,
                "```",
                "",
            ])

    lines.extend([
        "---",
        "",
        "## Remediation",
        "",
        "For each finding:",
        "1. Immediately revoke/rotate the exposed credential",
        "2. Remove the secret from source code",
        "3. Use environment variables or a secrets manager",
        "4. Clean git history if necessary",
        "5. Set up pre-commit hooks to prevent future leaks",
        "",
    ])

    return "\n".join(lines)


def format_sarif(findings: List[Finding], summary: Dict) -> str:
    """Format findings as SARIF for GitHub Security integration."""
    sarif = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "Secret Scanner",
                    "version": "1.0.0",
                    "informationUri": "https://github.com/1Mangesh1/dev-skills",
                    "rules": []
                }
            },
            "results": []
        }]
    }

    rules = {}
    results = []

    for finding in findings:
        rule_id = finding.secret_type
        if rule_id not in rules:
            rules[rule_id] = {
                "id": rule_id,
                "name": finding.pattern_name,
                "shortDescription": {"text": f"{finding.provider} secret detected"},
                "defaultConfiguration": {
                    "level": "error" if finding.severity in ["critical", "high"] else "warning"
                }
            }

        results.append({
            "ruleId": rule_id,
            "level": "error" if finding.severity in ["critical", "high"] else "warning",
            "message": {
                "text": f"Potential {finding.provider} secret found: {finding.pattern_name}"
            },
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": finding.file},
                    "region": {
                        "startLine": finding.line,
                        "startColumn": finding.column
                    }
                }
            }],
            "fingerprints": {
                "primary": finding.value_hash
            }
        })

    sarif["runs"][0]["tool"]["driver"]["rules"] = list(rules.values())
    sarif["runs"][0]["results"] = results

    return json.dumps(sarif, indent=2)


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Scan files for hardcoded secrets, API keys, and credentials"
    )
    parser.add_argument(
        "path",
        help="File or directory to scan"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "markdown", "sarif"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Write output to file"
    )
    parser.add_argument(
        "--severity", "-s",
        choices=["info", "low", "medium", "high", "critical"],
        default="info",
        help="Minimum severity to report (default: info)"
    )
    parser.add_argument(
        "--entropy",
        type=float,
        default=4.5,
        help="Entropy threshold for detection (default: 4.5)"
    )
    parser.add_argument(
        "--no-entropy",
        action="store_true",
        help="Disable entropy-based detection"
    )
    parser.add_argument(
        "--allowlist",
        help="Path to allowlist YAML file"
    )

    args = parser.parse_args()

    # Load allowlist if specified
    allowlist_patterns = []
    if args.allowlist:
        try:
            import yaml
            with open(args.allowlist) as f:
                config = yaml.safe_load(f)
                allowlist_patterns = config.get('patterns', [])
        except Exception as e:
            print(f"Warning: Could not load allowlist: {e}", file=sys.stderr)

    # Map severity string to enum
    severity_map = {
        "info": Severity.INFO,
        "low": Severity.LOW,
        "medium": Severity.MEDIUM,
        "high": Severity.HIGH,
        "critical": Severity.CRITICAL,
    }

    # Create scanner
    scanner = SecretScanner(
        entropy_threshold=args.entropy,
        enable_entropy=not args.no_entropy,
        min_severity=severity_map[args.severity],
        allowlist_patterns=allowlist_patterns,
    )

    # Run scan
    print(f"Scanning {args.path}...", file=sys.stderr)
    findings = scanner.scan_path(args.path)
    summary = scanner.get_summary()

    print(f"Found {len(findings)} potential secrets in {summary['files_scanned']} files", file=sys.stderr)

    # Format output
    if args.format == "json":
        output = format_json(findings, summary)
    elif args.format == "sarif":
        output = format_sarif(findings, summary)
    else:
        output = format_markdown(findings, summary)

    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Results written to {args.output}", file=sys.stderr)
    else:
        print(output)

    # Exit with error code if findings found
    if findings:
        critical_high = [f for f in findings if f.severity in ['critical', 'high']]
        if critical_high:
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
