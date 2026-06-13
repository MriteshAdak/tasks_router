from enum import StrEnum

class SSLMode(StrEnum):
    """Enum of supported PostgreSQL SSL connection modes."""

    DISABLE = "disable"
    ALLOW = "allow"
    PREFER = "prefer"
    REQUIRE = "require"
    VERIFY_CA = "verify-ca"
    VERIFY_FULL = "verify-full"