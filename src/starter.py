from .server import create_app

app = create_app()
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=app.config.PORT,
        dev=app.config.DEV,
        fast=not app.config.DEV,
        access_log=app.config.DEV,
    )
