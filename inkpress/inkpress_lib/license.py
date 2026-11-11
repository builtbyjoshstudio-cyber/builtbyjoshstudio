#!/usr/bin/env python3
"""
license.py — zero-dependency offline Pro license key generator and verifier.

Keys have the shape:
    INKP-XXXX-XXXX-XXXX-XXXX

Each 16-character RFC-4648 Base32 payload encodes 10 bytes (80 bits):
    byte 0      protocol version (0x01)
    byte 1      plan code (0x50 = 'P' Studio Pro, 0x46 = 'F' Founder Edition)
    bytes 2..3  16-bit buyer fingerprint derived from buyer email/order ID
    bytes 4..9  48-bit HMAC-SHA256 tag over bytes 0..3

Verification is 100% offline with zero network calls or external packages.

Owner CLI usage (to mint keys for Gumroad / LemonSqueezy / Stripe buyers):
    python -m inkpress_lib.license --mint buyer@example.com
    python -m inkpress_lib.license --verify INKP-XXXX-XXXX-XXXX-XXXX
"""
import argparse
import base64
import hashlib
import hmac
import json
import os
import re
import sys
from pathlib import Path

KEY_PREFIX = "INKP"
_PROTOCOL_VERSION = 1
_PLAN_CODES = {
    "PRO": ord("P"),
    "FOUNDER": ord("F"),
}
_CODE_TO_PLAN = {code: name for name, code in _PLAN_CODES.items()}

# Studio signing seed used for offline HMAC-SHA256 verification.
# Override with INKPRESS_LICENSE_SECRET env var if rotating keys for a custom fork.
_DEFAULT_SIGNING_MATERIAL = b"BuiltByJoshStudio::InkpressStudioPro::v1::OfflineKey2026"
_CLEAN_KEY_RE = re.compile(r"[^A-Z2-7]")


def _signing_key():
    override = os.environ.get("INKPRESS_LICENSE_SECRET", "").strip()
    if override:
        return override.encode("utf-8")
    return _DEFAULT_SIGNING_MATERIAL


def generate_key(buyer_id="studio@builtbyjoshstudio.com", plan="PRO"):
    """Mint a deterministic offline license key for buyer_id."""
    plan_norm = str(plan or "PRO").strip().upper()
    if plan_norm not in _PLAN_CODES:
        raise ValueError(f"unknown license plan {plan!r}; choose from {tuple(_PLAN_CODES)}")

    buyer_norm = str(buyer_id or "buyer").strip().lower().encode("utf-8")
    fingerprint = hashlib.sha256(b"inkpress-buyer:" + buyer_norm).digest()[:2]
    header = bytes([_PROTOCOL_VERSION, _PLAN_CODES[plan_norm]]) + fingerprint
    tag = hmac.new(_signing_key(), header, hashlib.sha256).digest()[:6]
    token = base64.b32encode(header + tag).decode("ascii")
    groups = [token[i : i + 4] for i in range(0, 16, 4)]
    return f"{KEY_PREFIX}-" + "-".join(groups)


def verify_key(raw_key):
    """Verify an INKP-XXXX-XXXX-XXXX-XXXX key.

    Returns a dict {'valid': True, 'plan': 'PRO', 'key': normalized_key, 'fingerprint': hex}
    if authentic, or None if invalid.
    """
    if not raw_key:
        return None
    text = str(raw_key).strip().upper()
    if text.startswith(f"{KEY_PREFIX}-"):
        text = text[len(KEY_PREFIX) + 1 :]
    elif text.startswith(KEY_PREFIX):
        text = text[len(KEY_PREFIX) :]

    # Normalize common user lookalike typos (0->O, 1->I) before Base32 decode.
    text = text.replace("0", "O").replace("1", "I")
    compact = _CLEAN_KEY_RE.sub("", text)
    if len(compact) != 16:
        return None

    try:
        raw_bytes = base64.b32decode(compact, casefold=True)
    except Exception:  # noqa: BLE001
        return None

    if len(raw_bytes) != 10:
        return None

    version = raw_bytes[0]
    plan_code = raw_bytes[1]
    if version != _PROTOCOL_VERSION or plan_code not in _CODE_TO_PLAN:
        return None

    header = raw_bytes[:4]
    provided_tag = raw_bytes[4:]
    expected_tag = hmac.new(_signing_key(), header, hashlib.sha256).digest()[:6]
    if not hmac.compare_digest(provided_tag, expected_tag):
        return None

    groups = [compact[i : i + 4] for i in range(0, 16, 4)]
    normalized = f"{KEY_PREFIX}-" + "-".join(groups)
    return {
        "valid": True,
        "plan": _CODE_TO_PLAN[plan_code],
        "key": normalized,
        "fingerprint": raw_bytes[2:4].hex().upper(),
    }


def default_license_path():
    """Return the user-level license file path (~/.inkpress_license.json)."""
    env_path = os.environ.get("INKPRESS_LICENSE_FILE", "").strip()
    if env_path:
        return Path(env_path)
    return Path.home() / ".inkpress_license.json"


def load_saved_license(license_path=None):
    """Load and verify the saved Studio license, or return None if on Free tier."""
    path = Path(license_path) if license_path else default_license_path()
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    verified = verify_key(data.get("key", ""))
    if not verified:
        return None
    if data.get("email"):
        verified["email"] = str(data["email"]).strip()
    return verified


def save_license(raw_key, email="", license_path=None):
    """Verify and persist a license key. Raises ValueError if invalid."""
    verified = verify_key(raw_key)
    if not verified:
        raise ValueError("Invalid Inkpress Pro license key. Expected INKP-XXXX-XXXX-XXXX-XXXX.")
    path = Path(license_path) if license_path else default_license_path()
    payload = {
        "key": verified["key"],
        "plan": verified["plan"],
        "email": str(email or "").strip(),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    verified["email"] = payload["email"]
    return verified


def clear_license(license_path=None):
    """Remove saved license file (returns app to Free Starter mode)."""
    path = Path(license_path) if license_path else default_license_path()
    try:
        if path.is_file():
            path.unlink()
    except OSError:
        pass


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="python -m inkpress_lib.license",
        description="Mint or verify offline Inkpress Studio Pro license keys.",
    )
    parser.add_argument("--mint", metavar="EMAIL", help="generate a Pro key for buyer email/order ID")
    parser.add_argument(
        "--plan",
        choices=sorted(_PLAN_CODES),
        default="PRO",
        help="license tier to encode when minting (default: PRO)",
    )
    parser.add_argument("--verify", metavar="KEY", help="verify an INKP-... license key")
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    if args.mint:
        key = generate_key(args.mint, plan=args.plan)
        print(f"Buyer:   {args.mint}")
        print(f"Plan:    Inkpress Studio {args.plan}")
        print(f"License: {key}")
        return 0

    if args.verify:
        info = verify_key(args.verify)
        if not info:
            print("INVALID license key", file=sys.stderr)
            return 1
        print(f"VALID — Plan: {info['plan']} | Key: {info['key']} | ID: {info['fingerprint']}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
