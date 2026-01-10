import random

# --- PUBLIC PARAMETERS (Shared Knowledge) ---
# In a real production app, use RFC 5114 2048-bit primes.
# For this demo/thesis, we use smaller primes to keep JS math fast and readable.
PRIME_P = 2695139  # A large prime number
GENERATOR_G = 2    # A generator

class ZKPVerifier:
    """
    Implements the Verifier side of the algorithm from Section 3.5
    """
    
    @staticmethod
    def generate_challenge():
        """Step 3: Verifier generates a random challenge c"""
        return random.randint(1, PRIME_P - 1)

    @staticmethod
    def verify_proof(public_key_y, commitment_t, challenge_c, response_s):
        """
        Step 5: Verifier Validates
        Formula: t' = (g^s * y^(-c)) mod p
        Note: In modular arithmetic, negative exponent is modular inverse.
        Equivalent check: (g^s) mod p == (t * y^c) mod p
        """
        # Calculate LHS: g^s mod p
        lhs = pow(GENERATOR_G, response_s, PRIME_P)
        
        # Calculate RHS: (t * y^c) mod p
        rhs_part = pow(public_key_y, challenge_c, PRIME_P)
        rhs = (commitment_t * rhs_part) % PRIME_P
        
        return lhs == rhs

# These are helper functions for the Client (Simulated in Python tests, 
# but usually implemented in JS on the frontend).
class ZKPProver:
    """
    Implements the Prover side (Client).
    Used here for testing logic or server-side simulation.
    """
    @staticmethod
    def generate_private_key(password_hash_int):
        return password_hash_int % (PRIME_P - 1)

    @staticmethod
    def generate_public_key(private_key_x):
        return pow(GENERATOR_G, private_key_x, PRIME_P)