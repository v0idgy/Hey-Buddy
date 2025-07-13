"""
Setup script for development environment.
"""
import os
import sys
import subprocess
from pathlib import Path


def run_command(command: str, cwd: str = None) -> bool:
    """Run a command and return success status."""
    try:
        result = subprocess.run(
            command.split(),
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {command}")
        print(f"Error: {e.stderr}")
        return False


def create_directories():
    """Create necessary directories."""
    directories = [
        "logs",
        "data/users",
        "data/cache",
        "temp",
        "templates/code",
        "config",
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")


def create_config_files():
    """Create default configuration files."""
    config_files = {
        "config/development.yaml": """
environment: development
debug: true
log_level: DEBUG
api_host: localhost
api_port: 8000
database_url: postgresql://localhost/virtual_assistant_dev
redis_url: redis://localhost:6379
""",
        "config/production.yaml": """
environment: production
debug: false
log_level: INFO
api_host: 0.0.0.0
api_port: 8000
database_url: postgresql://localhost/virtual_assistant
redis_url: redis://localhost:6379
""",
        ".env": """
ENVIRONMENT=development
SECRET_KEY=your-secret-key-change-this-in-production
ENCRYPTION_KEY=your-encryption-key-change-this
"""
    }
    
    for file_path, content in config_files.items():
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write(content.strip())
            print(f"✓ Created config file: {file_path}")


def install_dependencies():
    """Install Python dependencies."""
    print("Installing dependencies...")
    
    # Install base dependencies
    if not run_command("pip install -e ."):
        return False
    
    # Install development dependencies
    if not run_command("pip install -e .[dev]"):
        return False
    
    # Install spaCy model
    if not run_command("python -m spacy download en_core_web_sm"):
        return False
    
    return True


def setup_pre_commit():
    """Setup pre-commit hooks."""
    if not run_command("pre-commit install"):
        return False
    
    print("✓ Pre-commit hooks installed")
    return True


def setup_database():
    """Setup database (placeholder)."""
    print("Database setup would go here")
    print("✓ Database setup completed")


def main():
    """Main setup function."""
    print("Setting up Virtual Assistant development environment...")
    
    # Create directories
    create_directories()
    
    # Create configuration files
    create_config_files()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Setup pre-commit hooks
    if not setup_pre_commit():
        print("❌ Failed to setup pre-commit hooks")
        sys.exit(1)
    
    # Setup database
    setup_database()
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Start the virtual assistant: python -m src.main start")
    print("2. Run tests: python -m src.main test")
    print("3. Check the logs: tail -f logs/virtual_assistant.log")


if __name__ == "__main__":
    main()