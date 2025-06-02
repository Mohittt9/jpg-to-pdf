from PIL import Image
import os

# All user sessions and images are managed here.
# Implement persistent storage (e.g., JSON, sqlite) for sessions.

def handle_image(update, context):
    """Handle receiving an image from user. Save to temp, add to their session."""
    pass

async def list_images(update, context):
    """List all images in user's session."""
    pass

async def remove_image(update, context):
    """Remove an image by its index in user's session."""
    pass

async def move_image(update, context):
    """Reorder images in user's session."""
    pass

async def show_stats(update, context):
    """Show user's usage statistics."""
    pass

def get_user_images(user_id):
    """Return list of image filepaths for user."""
    pass

def cleanup_user_session(user_id):
    """Remove all temp files and session data for user."""
    pass