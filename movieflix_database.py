"""SQLite authentication layer for the MovieFlix Streamlit app.

This file keeps all database and password-security logic separate from the UI.
It uses only Python standard-library modules, so you do not need MySQL/MongoDB
for a university/demo project. Data is saved in movieflix_users.db.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path(os.getenv("MOVIEFLIX_DB_PATH", "movieflix_users.db"))
PBKDF2_ITERATIONS = 260_000
RESET_CODE_EXPIRY_MINUTES = 10


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create required tables if they do not already exist."""
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS password_resets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                code_hash TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                used INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        conn.commit()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def _row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row is not None else None


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256 with a random salt."""
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return "pbkdf2_sha256${}${}${}".format(
        PBKDF2_ITERATIONS,
        base64.b64encode(salt).decode("ascii"),
        base64.b64encode(digest).decode("ascii"),
    )


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against the stored PBKDF2 hash."""
    try:
        algorithm, iterations, salt_b64, digest_b64 = stored_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        salt = base64.b64decode(salt_b64.encode("ascii"))
        stored_digest = base64.b64decode(digest_b64.encode("ascii"))
        candidate_digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            int(iterations),
        )
        return hmac.compare_digest(candidate_digest, stored_digest)
    except Exception:
        return False


def username_exists(username: str) -> bool:
    with _connect() as conn:
        row = conn.execute(
            "SELECT id FROM users WHERE username = ? COLLATE NOCASE",
            (username.strip(),),
        ).fetchone()
    return row is not None


def email_exists(email: str) -> bool:
    with _connect() as conn:
        row = conn.execute(
            "SELECT id FROM users WHERE email = ? COLLATE NOCASE",
            (email.strip().lower(),),
        ).fetchone()
    return row is not None


def get_user_by_login(identifier: str) -> dict[str, Any] | None:
    """Return a user by username OR email."""
    identifier = identifier.strip()
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT * FROM users
            WHERE username = ? COLLATE NOCASE OR email = ? COLLATE NOCASE
            """,
            (identifier, identifier.lower()),
        ).fetchone()
    return _row_to_dict(row)


def get_user_by_email(email: str) -> dict[str, Any] | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ? COLLATE NOCASE",
            (email.strip().lower(),),
        ).fetchone()
    return _row_to_dict(row)


def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return _row_to_dict(row)


def create_user(username: str, email: str, password: str) -> tuple[bool, str]:
    """Create a user and return (success, message)."""
    username = username.strip()
    email = email.strip().lower()

    if username_exists(username):
        return False, "Username already exists. Please choose another username."
    if email_exists(email):
        return False, "Email address already exists. Please login or use another email."

    now = _iso(_utc_now())
    try:
        with _connect() as conn:
            conn.execute(
                """
                INSERT INTO users (username, email, password_hash, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (username, email, hash_password(password), now, now),
            )
            conn.commit()
        return True, "Account created successfully. Please login."
    except sqlite3.IntegrityError:
        return False, "This username or email is already registered."
    except Exception as exc:
        return False, f"Database error: {exc}"


def authenticate_user(identifier: str, password: str) -> tuple[bool, str, dict[str, Any] | None]:
    """Authenticate by username/email and password."""
    user = get_user_by_login(identifier)
    if not user:
        return False, "No account found with this username or email. Please signup first.", None

    if not verify_password(password, user["password_hash"]):
        return False, "Incorrect password. Please try again.", None

    safe_user = {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "created_at": user["created_at"],
    }
    return True, "Login successful.", safe_user


def create_reset_code(email: str) -> tuple[bool, str, str | None]:
    """Create a 6-digit reset code for a registered email.

    Returns (success, message, plain_code). The plain code is returned only so the
    UI can email it; only its hash is stored in SQLite.
    """
    user = get_user_by_email(email)
    if not user:
        return False, "No registered account found with this email address.", None

    code = f"{secrets.randbelow(1_000_000):06d}"
    now = _utc_now()
    expires_at = now + timedelta(minutes=RESET_CODE_EXPIRY_MINUTES)

    with _connect() as conn:
        conn.execute(
            "UPDATE password_resets SET used = 1 WHERE user_id = ? AND used = 0",
            (user["id"],),
        )
        conn.execute(
            """
            INSERT INTO password_resets (user_id, code_hash, expires_at, used, created_at)
            VALUES (?, ?, ?, 0, ?)
            """,
            (user["id"], hash_password(code), _iso(expires_at), _iso(now)),
        )
        conn.commit()

    return True, "Verification code generated successfully.", code


def reset_password(email: str, code: str, new_password: str) -> tuple[bool, str]:
    """Verify the latest active reset code and set a new password."""
    user = get_user_by_email(email)
    if not user:
        return False, "No registered account found with this email address."

    with _connect() as conn:
        row = conn.execute(
            """
            SELECT * FROM password_resets
            WHERE user_id = ? AND used = 0
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (user["id"],),
        ).fetchone()

        if not row:
            return False, "No active reset code found. Please request a new code."

        expires_at = datetime.fromisoformat(row["expires_at"])
        if _utc_now() > expires_at:
            conn.execute(
                "UPDATE password_resets SET used = 1 WHERE id = ?",
                (row["id"],),
            )
            conn.commit()
            return False, "Reset code has expired. Please request a new code."

        if not verify_password(code.strip(), row["code_hash"]):
            return False, "Invalid verification code. Please check your email and try again."

        now = _iso(_utc_now())
        conn.execute(
            "UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
            (hash_password(new_password), now, user["id"]),
        )
        conn.execute(
            "UPDATE password_resets SET used = 1 WHERE id = ?",
            (row["id"],),
        )
        conn.commit()

    return True, "Password reset successful. Please login with your new password."
