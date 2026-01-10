import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login as django_login, logout as django_logout
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from .models import ZKPProfile
from .zkp_utils import ZKPVerifier, PRIME_P, GENERATOR_G

def register_view(request):
    if request.method == 'GET':
        return render(request, 'auth/register.html', {
            'prime_p': PRIME_P, 
            'generator_g': GENERATOR_G
        })
    
    # Process ZKP Registration (Receive Public Key)
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        public_key = data.get('public_key') # 'y' calculated by client

        if User.objects.filter(username=username).exists():
            return JsonResponse({'status': 'error', 'message': 'Username exists'})

        # Create standard Django user (password is unusable/random)
        user = User.objects.create_user(username=username, password=None)
        # Store ZKP Public Key
        ZKPProfile.objects.create(user=user, public_key=public_key)
        
        return JsonResponse({'status': 'success', 'redirect': reverse('login')})

def login_view(request):
    return render(request, 'auth/login.html', {
        'prime_p': PRIME_P,
        'generator_g': GENERATOR_G
    })

def logout_view(request):
    django_logout(request)
    return redirect('home')

# --- The Interactive ZKP Authentication API ---

@csrf_exempt
def zkp_challenge(request):
    """
    Step 1 & 2 of Authentication:
    Client sends Username + Commitment (t).
    Server checks user, stores (t), generates Challenge (c), sends (c).
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        commitment_t = int(data.get('commitment_t'))

        try:
            user = User.objects.get(username=username)
            # Generate Challenge
            challenge_c = ZKPVerifier.generate_challenge()
            
            # Save state in session for Step 3
            request.session['auth_zkp_user_id'] = user.id
            request.session['auth_zkp_commitment_t'] = commitment_t
            request.session['auth_zkp_challenge_c'] = challenge_c
            
            return JsonResponse({
                'status': 'challenge_issued',
                'challenge_c': challenge_c
            })
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'})

@csrf_exempt
def zkp_verify(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        response_s = int(data.get('response_s'))

        user_id = request.session.get('auth_zkp_user_id')
        commitment_t = request.session.get('auth_zkp_commitment_t')
        challenge_c = request.session.get('auth_zkp_challenge_c')

        if not user_id or not commitment_t or not challenge_c:
            return JsonResponse({'status': 'error', 'message': 'Session expired'})

        user = User.objects.get(id=user_id)
        public_key_y = int(user.zkpprofile.public_key)

        # --- Manual Verification Steps for Logging ---
        # Formula: g^s == t * y^c (mod p)
        
        # LHS: g^s mod p
        lhs = pow(GENERATOR_G, response_s, PRIME_P)
        
        # RHS: (t * y^c) mod p
        rhs_part = pow(public_key_y, challenge_c, PRIME_P)
        rhs = (commitment_t * rhs_part) % PRIME_P
        
        is_valid = (lhs == rhs)

        if is_valid:
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            django_login(request, user)
            return JsonResponse({
                'status': 'success', 
                'redirect': '/',
                # Send back math details for the visual logger
                'debug': {
                    'lhs': lhs,
                    'rhs': rhs,
                    'public_key_y': public_key_y,
                    'challenge_c': challenge_c
                }
            })
        else:
            return JsonResponse({
                'status': 'error', 
                'message': 'Zero-Knowledge Proof Failed!',
                'debug': {
                    'lhs': lhs,
                    'rhs': rhs
                }
            })