# django-zkp-auth

A reusable Django authentication app implementing the **Schnorr Interactive Zero-Knowledge Proof** protocol. The user's passphrase never leaves their browser — only a derived public key is stored on the server.

---

## Installation

```bash
pip install django-zkp-auth
```

---

## Quick Start

### 1. Add to `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    ...
    'authentication',
]
```

### 2. Include the URLs

In your root `urls.py`, include the authentication URLs under the `auth/` prefix:

```python
from django.urls import path, include

urlpatterns = [
    path('auth/', include('authentication.urls')),
    ...
]
```

### 3. Run migrations

```python
python manage.py migrate
```

### 4. Configure login redirects (optional)

The app uses Django's standard redirect settings. Add these to your `settings.py` as needed:

```python
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'   # where to redirect after login
LOGOUT_REDIRECT_URL = 'home'  # where to redirect after logout
```

---

## URL Reference

All routes are served under whichever prefix you chose (e.g. `auth/`):

| URL | Name | Description |
|-----|------|-------------|
| `auth/register/` | `register` | Registration page |
| `auth/login/` | `login` | Login page |
| `auth/logout/` | `logout` | Logs the user out |
| `auth/challenge/` | `zkp_challenge` | API — Step 2: issues ZKP challenge |
| `auth/verify/` | `zkp_verify` | API — Step 4: verifies ZKP proof |

---

## How It Works

Registration and login follow the Schnorr Interactive ZKP protocol:

### Registration

1. Client derives private key: `x = SHA256(passphrase) % (P - 1)`
2. Client computes public key: `y = G^x mod P`
3. Client sends only `y` (and `username`) to the server — the passphrase is never transmitted
4. Server creates a Django `User` with an unusable password and stores `y` in a `ZKPProfile`

### Login (Interactive Proof)

1. **Client → Server** (`auth/challenge/`): Client picks random nonce `r`, computes commitment `t = G^r mod P`, sends `username` and `t`
2. **Server → Client**: Generates random challenge `c`, stores `(user_id, t, c)` in the session, returns `c`
3. **Client → Server** (`auth/verify/`): Computes response `s = (r + c * x) % (P - 1)`, sends `s`
4. **Server**: Verifies `G^s ≡ t · y^c (mod P)` — if true, the user is authenticated

The public parameters used are:

```python
PRIME_P     = 2695139  # intentionally small for readability; see note below
GENERATOR_G = 2
```

> **Production note:** The default prime is intentionally small for demonstration purposes. For production, replace `PRIME_P` with a 2048-bit safe prime from RFC 3526 or NIST recommendations by editing `authentication/zkp_utils.py`.

---

## Data Model

```python
class ZKPProfile(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE)
    public_key = models.CharField(max_length=255)  # stores 'y'
```

---

## API Endpoints

### `POST auth/challenge/`

Request body (JSON):

```json
{ "username": "alice", "commitment_t": 1234567 }
```

Success response:

```json
{ "status": "challenge_issued", "challenge_c": 891234 }
```

Error response:

```json
{ "status": "error", "message": "User not found" }
```

### `POST auth/verify/`

Request body (JSON):

```json
{ "response_s": 2301984 }
```

Success response:

```json
{
  "status": "success",
  "redirect": "/",
  "debug": {
    "lhs": 123456,
    "rhs": 123456,
    "public_key_y": 654321,
    "challenge_c": 891234
  }
}
```

Error response:

```json
{
  "status": "error",
  "message": "Zero-Knowledge Proof Failed!",
  "debug": { "lhs": 111, "rhs": 222 }
}
```

> **Note:** Both API endpoints use `@csrf_exempt`. Ensure your client includes the session cookie for the verify step, as the server reads `(user_id, t, c)` from the session set during the challenge step.

---

## Template Customisation

Templates are located at `templates/auth/`. To override them, create your own versions at the same paths inside your project's template directories:

```
templates/
  auth/
    login.html
    register.html
```

Both templates receive the following context variables from their views:

| Variable | Value |
|----------|-------|
| `prime_p` | `PRIME_P` (2695139) |
| `generator_g` | `GENERATOR_G` (2) |

The base template (`blog/templates/blog/base.html`) exposes one block for content override:

```html
{% block content %}{% endblock %}
```

---

## Utility Classes

### `ZKPVerifier`

Server-side verification helpers (in `authentication/zkp_utils.py`):

```python
from authentication.zkp_utils import ZKPVerifier

# Generate a random challenge integer in [1, P-1]
c = ZKPVerifier.generate_challenge()

# Verify the proof: returns True if G^s ≡ t·y^c (mod P)
valid = ZKPVerifier.verify_proof(
    public_key_y=y,
    commitment_t=t,
    challenge_c=c,
    response_s=s
)
```

### `ZKPProver`

Client-side helpers (primarily for testing and server-side simulation):

```python
from authentication.zkp_utils import ZKPProver

# Derive private key from a SHA-256 hash integer
x = ZKPProver.generate_private_key(password_hash_int)

# Compute public key
y = ZKPProver.generate_public_key(x)
```

---

## Demo Data

A management command is included to populate the database with demo users and blog posts:

```bash
python manage.py populate_db
```

This creates 15 users (e.g. `neo`, `trinity`, `morpheus`) all with password `password123`, plus 25 sample blog posts.

---

## License

MIT
