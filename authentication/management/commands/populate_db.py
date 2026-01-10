import random
import hashlib
import io
import base64
from PIL import Image, ImageDraw # Requires: pip install Pillow

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from authentication.models import ZKPProfile
from blog.models import Post
from authentication.zkp_utils import PRIME_P, GENERATOR_G

class Command(BaseCommand):
    help = 'Populates the database with Cyberpunk users and posts with generated drawings'

    def generate_scribble(self):
        """
        Generates a random black-on-white scribble image and returns it as a Base64 string.
        """
        width, height = 600, 300
        # Create white background
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)

        # Draw 3 to 6 separate "strokes"
        for _ in range(random.randint(3, 6)):
            # Pick a random starting point
            current_x = random.randint(50, width - 50)
            current_y = random.randint(50, height - 50)
            
            # Draw a connected line with 10 to 20 segments
            for _ in range(random.randint(10, 20)):
                # Calculate next point (random walk)
                next_x = current_x + random.randint(-60, 60)
                next_y = current_y + random.randint(-60, 60)
                
                # Keep within bounds (clamping)
                next_x = max(0, min(width, next_x))
                next_y = max(0, min(height, next_y))

                # Draw the segment
                draw.line(
                    (current_x, current_y, next_x, next_y), 
                    fill='black', 
                    width=random.randint(2, 4)
                )
                
                # Move cursor
                current_x, current_y = next_x, next_y

        # Convert to Base64
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return f"data:image/png;base64,{img_str}"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Deleting old data...'))
        
        # Clean slate
        Post.objects.all().delete()
        ZKPProfile.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        # --- CONFIGURATION ---
        DEFAULT_PASSWORD = "password123"
        
        users_data = [
            "Neo", "Trinity", "Morpheus", "Case", "MollyMillions", 
            "HiroProtagonist", "Deckard", "MajorKusanagi", "Flynn", "Tron",
            "Satoshi", "Cipher", "Switch", "Tank", "Dozer"
        ]

        titles = [
            "Signal Lost in Sector 7",
            "The Wintermute Protocol",
            "Glitch in the Reality Render",
            "Neural Link Latency Issues",
            "Encryption Keys for the Black Market",
            "Is the Oracle an AI?",
            "Cybernetic Limb Maintenance 101",
            "Escaping the Grid",
            "Memories of a Replicant",
            "Zero-Knowledge Proofs explained to a Construct",
            "Hard Reset Required",
            "Blue Pill or Red Pill?",
            "Analyzing the Source Code"
        ]

        contents = [
            "The sky above the port was the color of television, tuned to a dead channel. I tried to access the mainframe but the ICE was too thick.",
            "We are seeing anomalies in the ZKP handshake protocol. Someone is trying to brute force the discrete logarithm problem using quantum annealing.",
            "Just upgraded my deck to the Ono-Sendai Cyberspace 7. The render speeds are insane, but it overheats like a nuclear reactor.",
            "Remember: Trust no one. Verify everything. Privacy is the only currency that matters in this digital wasteland.",
            "I found a backdoor in the corporate subnet. It looks like they are hiding data about the project. Downloading now...",
            "Does anyone else feel like we are living in a simulation? The physics engine glitched yesterday when I dropped my coffee.",
            "My public key was rejected by the server node. I think I'm being tracked by an Agent.",
            "Looking for a crew for a data heist. Must have experience with Schnorr signatures and Django backends."
        ]

        self.stdout.write(self.style.SUCCESS(f'Generating {len(users_data)} Users...'))

        created_users = []

        # 1. Create Users & ZKP Profiles
        for username in users_data:
            # Emulate Client-Side Logic in Python
            
            # Hash password to integer
            pass_bytes = DEFAULT_PASSWORD.encode('utf-8')
            pass_hash = hashlib.sha256(pass_bytes).hexdigest()
            pass_int = int(pass_hash, 16)

            # Calculate Private Key x
            x = pass_int % (PRIME_P - 1)

            # Calculate Public Key y = g^x mod p
            y = pow(GENERATOR_G, x, PRIME_P)

            # Create DB Entries
            user = User.objects.create_user(username=username, password=None) # No password stored
            ZKPProfile.objects.create(user=user, public_key=str(y))
            
            created_users.append(user)

        self.stdout.write(self.style.SUCCESS('Generating Posts with Drawings...'))

        # 2. Create Random Posts
        for i in range(25): # Generate 25 posts
            author = random.choice(created_users)
            title = random.choice(titles)
            content = random.choice(contents)
            
            # Generate a unique drawing for this post
            drawing_data = self.generate_scribble()

            Post.objects.create(
                author=author,
                title=title,
                content=content,
                drawing_data=drawing_data
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated database with Cyberpunk data!'))
        self.stdout.write(self.style.MIGRATE_HEADING(f'Default Password for all users: "{DEFAULT_PASSWORD}"'))