import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-this-secret-key")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = [host.strip() for host in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.core.apps.CoreConfig",
    "apps.bookings.apps.BookingsConfig",
    "apps.accounts.apps.AccountsConfig", 
    "apps.epk.apps.EpkConfig",
    "apps.music.apps.MusicConfig",
    "apps.download.apps.DownloadConfig",
    "apps.events.apps.EventsConfig",
    "apps.subscribers.apps.SubscribersConfig",
    "apps.notifications.apps.NotificationsConfig",
    "apps.dashboard.apps.DashboardConfig",
    "django.contrib.sites", 


    # allauth
    "allauth",
    "allauth.account",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",   # <-- add this

]


AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# allauth behaviour (current names, allauth >= 65)
ACCOUNT_LOGIN_METHODS = {"email", "username"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_UNIQUE_EMAIL = True
LOGIN_REDIRECT_URL = "/music/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"

ROOT_URLCONF = "config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {
        "context_processors": [
            "django.template.context_processors.debug",
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ],
    },
}]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


AUTH_USER_MODEL = "accounts.User"


LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Kampala"
USE_I18N = True
USE_TZ = True

# ============================================================
# STATIC FILES
# ============================================================

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"


# ============================================================
# USER UPLOADED MEDIA
# ============================================================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ============================================================
# EMAIL
# ============================================================
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",  # dev default
)

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "False").lower() == "true"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_TIMEOUT = int(os.getenv("EMAIL_TIMEOUT", "10"))

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL", "DJ Artist <noreply@example.com>"
)
SERVER_EMAIL = DEFAULT_FROM_EMAIL  # used for error reports to ADMINS

# Who gets crash emails when DEBUG=False
ADMINS = [("Admin", os.getenv("ADMIN_EMAIL", "you@example.com"))]

SITE_URL = os.getenv("SITE_URL", "http://127.0.0.1:8000")



SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
X_FRAME_OPTIONS = "SAMEORIGIN"



MUSIC_EMBED_ALLOWED_HOSTS = [
    "bandcamp.com",
    "player.vimeo.com",
]



# ============================================================
# AUTH REDIRECTS
# ============================================================
# Every @login_required view bounces here when a guest is unauthenticated.
LOGIN_URL = "account_login"

# Where allauth sends users after successful login.
LOGIN_REDIRECT_URL = "/epk/official/"     # ✅ points at a specific kit
LOGIN_REDIRECT_URL_FALLBACK = "/"       # optional extra safety

# Where users land after logout.
LOGOUT_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"

# Dashboard-specific (staff) redirects stay scoped to the dashboard app.
# If you need a staff-only login at /dashboard/login/, give that view
# its own decorator with login_url="dashboard:login" — do NOT set it as
# the global LOGIN_URL.



from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG:   "secondary",
    messages.INFO:    "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR:   "danger",
}

ACCOUNT_ADAPTER = "apps.accounts.adapters.AccountAdapter"