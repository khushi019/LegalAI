#!/usr/bin/env python
"""
Setup script for LegalDoc AI.
This script runs migrations and creates a superuser if one doesn't exist.
"""
import os
import sys
import django
from django.contrib.auth.models import User

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'legaldoc_ai.settings')
django.setup()

def run_migrations():
    """Run Django migrations."""
    print("Running migrations...")
    from django.core.management import call_command
    call_command('makemigrations')
    call_command('migrate')
    print("Migrations complete.")

def create_superuser():
    """Create a superuser if one doesn't exist."""
    if not User.objects.filter(is_superuser=True).exists():
        print("Creating superuser...")
        username = input("Enter username (default: admin): ") or 'admin'
        email = input("Enter email: ")
        password = input("Enter password: ")
        
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Superuser '{username}' created successfully.")
    else:
        print("Superuser already exists.")

def create_legal_knowledge_dir():
    """Create directory for legal knowledge base if it doesn't exist."""
    knowledge_dir = os.path.join('data', 'legal_knowledge')
    if not os.path.exists(knowledge_dir):
        print("Creating legal knowledge directory...")
        os.makedirs(knowledge_dir, exist_ok=True)
        print("Legal knowledge directory created.")
    else:
        print("Legal knowledge directory already exists.")

def main():
    """Main function."""
    print("Setting up LegalDoc AI...")
    run_migrations()
    create_superuser()
    create_legal_knowledge_dir()
    print("Setup complete!")

if __name__ == "__main__":
    main() 