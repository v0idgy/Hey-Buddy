"""
Main entry point for the Virtual Assistant application.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
from loguru import logger

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from api.server import APIServer
from automation.automation_manager import AutomationManager
from gui.main_window import MainWindow
from nlp.command_parser import CommandParser
from voice.voice_processor import VoiceProcessor

from core.config import settings
from core.exceptions import VirtualAssistantError
from core.logging_config import setup_logging


class VirtualAssistant:
    """Main Virtual Assistant application class."""

    def __init__(self):
        self.voice_processor = None
        self.command_parser = None
        self.automation_manager = None
        self.api_server = None
        self.gui = None
        self.is_running = False

    async def initialize(self) -> None:
        """Initialize all components."""
        try:
            logger.info("Initializing Virtual Assistant...")

            # Initialize components
            self.voice_processor = VoiceProcessor()
            self.command_parser = CommandParser()
            self.automation_manager = AutomationManager()
            self.api_server = APIServer()

            # Initialize voice processor
            await self.voice_processor.initialize()

            # Initialize NLP components
            await self.command_parser.initialize()

            # Initialize automation manager
            await self.automation_manager.initialize()

            logger.info("Virtual Assistant initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Virtual Assistant: {e}")
            raise VirtualAssistantError(f"Initialization failed: {e}")

    async def start(self) -> None:
        """Start the Virtual Assistant."""
        try:
            if self.is_running:
                logger.warning("Virtual Assistant is already running")
                return

            logger.info("Starting Virtual Assistant...")

            # Start API server
            await self.api_server.start()

            # Start voice processing
            await self.voice_processor.start_listening()

            # Start automation manager
            await self.automation_manager.start()

            self.is_running = True
            logger.info("Virtual Assistant started successfully")

        except Exception as e:
            logger.error(f"Failed to start Virtual Assistant: {e}")
            raise VirtualAssistantError(f"Start failed: {e}")

    async def stop(self) -> None:
        """Stop the Virtual Assistant."""
        try:
            if not self.is_running:
                logger.warning("Virtual Assistant is not running")
                return

            logger.info("Stopping Virtual Assistant...")

            # Stop voice processing
            if self.voice_processor:
                await self.voice_processor.stop_listening()

            # Stop automation manager
            if self.automation_manager:
                await self.automation_manager.stop()

            # Stop API server
            if self.api_server:
                await self.api_server.stop()

            self.is_running = False
            logger.info("Virtual Assistant stopped successfully")

        except Exception as e:
            logger.error(f"Failed to stop Virtual Assistant: {e}")
            raise VirtualAssistantError(f"Stop failed: {e}")

    async def process_command(self, command: str) -> str:
        """Process a voice command."""
        try:
            # Parse command
            parsed_command = await self.command_parser.parse(command)

            # Execute command
            result = await self.automation_manager.execute_command(parsed_command)

            return result

        except Exception as e:
            logger.error(f"Failed to process command '{command}': {e}")
            return f"Sorry, I couldn't process that command: {e}"


# CLI Commands
@click.group()
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option("--config", type=click.Path(exists=True), help="Configuration file path")
def cli(debug: bool, config: Optional[str]):
    """Virtual Assistant CLI."""
    if debug:
        settings.debug = True
        settings.log_level = "DEBUG"

    if config:
        settings.config_path = config

    # Setup logging
    setup_logging(settings.log_level, settings.log_file)


@cli.command()
@click.option("--gui", is_flag=True, help="Start with GUI")
@click.option("--no-voice", is_flag=True, help="Disable voice processing")
def start(gui: bool, no_voice: bool):
    """Start the Virtual Assistant."""

    async def run():
        assistant = VirtualAssistant()

        try:
            await assistant.initialize()

            if gui:
                # Start with GUI
                assistant.gui = MainWindow(assistant)
                assistant.gui.show()

            if not no_voice:
                await assistant.start()

            # Keep running
            while assistant.is_running:
                await asyncio.sleep(1)

        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        except Exception as e:
            logger.error(f"Application error: {e}")
        finally:
            await assistant.stop()

    asyncio.run(run())


@cli.command()
def setup():
    """Setup the Virtual Assistant for first-time use."""
    from scripts.setup import setup_assistant

    setup_assistant()


@cli.command()
def test():
    """Run tests."""
    import subprocess

    result = subprocess.run(["pytest", "tests/"], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    sys.exit(result.returncode)


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
