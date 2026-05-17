from dotenv import load_dotenv
from split_settings.tools import include


load_dotenv()


include(
    'components/variables.py',
    'components/database.py',
    'components/installed_apps.py',
    'components/middleware.py',
    'components/templates.py',
    'components/auth_password_validators.py'
)
