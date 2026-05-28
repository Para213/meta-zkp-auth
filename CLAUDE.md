# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

META is a Django web application demonstrating Zero-Knowledge Proof (ZKP) authentication using the Schnorr Interactive Protocol. Users prove knowledge of a secret without transmitting passwords — only a mathematical proof is verified. The UI is cyberpunk-themed.

## Commands

```bash
# Run development server
python manage.py runserver

# Apply migrations
python manage.py migrate

# Populate demo database (15 cyberpunk users + 25 blog posts)
python manage.py populate_db

# Install dependencies
pip install -r requirements.txt
```

There is no test suite currently. Django's built-in test runner would be: `python manage.py test`.

## Architecture

Two Django apps under `meta-zkp-auth/`:

### `authentication/` — ZKP Auth System
- **`zkp_utils.py`**: Core crypto. Public params: `PRIME_P = 2695139`, `GENERATOR_G = 2` (demo values; comment references RFC 5114 for production). `ZKPVerifier` verifies server-side; `ZKPProver` is a client-side helper.
- **`models.py`**: `ZKPProfile` — OneToOne with Django `User`, stores public key `y = g^x mod p`.
- **`views.py`**: Two API endpoints for the interactive protocol:
  - `POST /auth/challenge/` — receives commitment `t`, returns challenge `c`, stores both in session.
  - `POST /auth/verify/` — receives proof `s`, verifies `g^s ≡ t·y^c (mod p)`, authenticates user on success.

### `blog/` — Content App
- `Post` model (title, content, optional base64 `drawing_data`, author FK).
- Standard CRUD views; `post_create` and `post_edit` require login. Full-text search on title/content.

### ZKP Login Flow (5 steps)
1. Client derives private key `x` from password via SHA-256, computes public key `y = g^x mod p` (stored at registration).
2. Client picks random nonce `r`, sends commitment `t = g^r mod p` to `/auth/challenge/`.
3. Server returns random challenge `c`.
4. Client computes proof `s = (r + c·x) mod (p-1)`, sends to `/auth/verify/`.
5. Server checks `g^s ≡ t·y^c (mod p)` — password never leaves the client.

The JavaScript in `templates/auth/login.html` uses native `BigInt` and `crypto.subtle.digest('SHA-256', ...)` to perform all client-side crypto. `modPow(base, exp, mod)` is implemented inline.

### Settings Notes
- `DEBUG = True`, SQLite database (`db.sqlite3`).
- `LOGIN_URL = 'login'`, `LOGIN_REDIRECT_URL = 'home'`, `LOGOUT_REDIRECT_URL = 'home'`.
- Templates: root `/templates/` directory + app-level templates.

## Demo Data
`populate_db` creates users with usernames like `neo`, `trinity`, `morpheus` — all with password `password123`. The login page defaults to showing `secret123` as placeholder; the actual demo password is `password123`.
