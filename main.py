from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

filterwarnings(
    action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning
)
filterwarnings(
    action="ignore", message=r".*the `days` parameter.*", category=PTBUserWarning
)
filterwarnings(
    action="ignore", message=r".*invalid escape sequence.*", category=SyntaxWarning
)

from handlers import setup_and_run_app

if __name__ == "__main__":
    setup_and_run_app()
