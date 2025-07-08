import os
import ssl
from pathlib import Path
from wsgiref.simple_server import make_server

from configurations.wsgi import get_wsgi_application
from watchfiles import run_process


def run_server():
    # Set Django environment
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    os.environ.setdefault("DJANGO_CONFIGURATION", "Development")
    application = get_wsgi_application()

    # Set certificate paths
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
    ssl_context.load_cert_chain(certfile="certs/djangotricks.local.pem", keyfile="certs/djangotricks.local-key.pem")

    # Run server with TLS
    with make_server("djangotricks.local", 8000, application) as httpd:
        httpd.socket = ssl_context.wrap_socket(httpd.socket, server_side=True)
        print("Serving on https://djangotricks.local:8000")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server stopped.")


if __name__ == "__main__":
    # Watch directories for changes
    watched_dirs = [
        str(Path(__file__).parent),  # Current directory
    ]

    # Start watching and run the server with auto-reload
    run_process(
        *watched_dirs,  # Paths to watch
        target=run_server,  # Function to run
        debounce=1600,  # Debounce changes (milliseconds)
        recursive=True,  # Watch directories recursively
        debug=True,  # Enable debug logging
    )
