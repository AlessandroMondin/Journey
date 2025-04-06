import uvicorn
import sys
import os

from config import API_SERVICE_URL, EXPOSE_PUBLICLY, logger
from urllib.parse import urlparse

# Parse the URL properly
parsed_url = urlparse(API_SERVICE_URL)
if parsed_url.netloc:  # If it's a full URL with scheme (http://)
    host = parsed_url.hostname
    port = parsed_url.port or 8000  # Default to 8000 if no port specified
else:  # If it's just hostname:port
    parts = API_SERVICE_URL.split(":")
    host = parts[0]
    port = int(parts[1]) if len(parts) > 1 else 8000

# Override with 0.0.0.0 to make accessible from external networks
if EXPOSE_PUBLICLY:
    host = "0.0.0.0"
    print(f"⚠️  Exposing API service publicly on {host}:{port}")
    print("⚠️  Anyone on your network can access this service!")

# Optional: Use ngrok for public URL tunneling
if EXPOSE_PUBLICLY:
    try:
        import pyngrok.ngrok as ngrok

        # Kill any existing ngrok processes first to avoid the
        # session limit error
        print("Terminating any existing ngrok processes...")
        # This ensures we don't hit the session limit by properly
        # closing previous sessions
        ngrok.kill()

        # Start ngrok tunnel with proper configuration
        print("Starting ngrok tunnel...")
        # Use proper configuration for newer pyngrok versions
        public_url = ngrok.connect(port).public_url
        print(f"🌐 Public URL: {public_url}")

        # Update environment variables for other services to use
        os.environ["PUBLIC_API_URL"] = public_url
        logger.info(f"Set PUBLIC_API_URL={public_url} for other services")
        print(f"PUBLIC_API_URL={public_url}")

        # Make sure the ngrok process gets killed when the application exits
        import atexit

        atexit.register(ngrok.kill)
    except ImportError:
        print("⚠️  To use ngrok tunneling, install pyngrok:")
        print("   pip install pyngrok")
        print("   Then set USE_NGROK=true to enable it")
        if "--raise-import-errors" in sys.argv:
            raise
    except Exception as e:
        print(f"⚠️  Failed to start ngrok tunnel: {e}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,
        workers=1,
    )
