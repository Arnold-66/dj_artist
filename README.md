# DJ Artist Platform

A Django-powered DJ artist website with bookings, EPK, music embeds, events, newsletter subscriptions and a staff dashboard.

## Requirements
- Python 3.12 or newer (Python 3.14 should work with a compatible Django 6.x release)
- Internet connection for Bootstrap CDN and configured SMTP email

## Windows setup

Open Command Prompt in this folder:

```cmd
py -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
python manage.py check
python manage.py makemigrations core bookings epk music events subscribers notifications
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open:
- Website: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/
- Staff dashboard: http://127.0.0.1:8000/dashboard/

## First-time content setup
1. Log in to `/admin/`.
2. Add an Artist profile under Core.
3. Add a Press Kit with slug `official`. For a private EPK, turn off `is_public`, set a password using the Django shell (instructions below), and save.
4. Add Press Images, then attach them to the Press Kit.
5. Add Events and Mixes. Use official embed URLs supplied by YouTube, SoundCloud or Audiomack.
6. Booking inquiries are collected at `/bookings/`.
7. Newsletter subscriptions are collected at `/subscribe/`.

## Set a private EPK password
Django admin does not expose the password hash field. Run:

```cmd
python manage.py shell
```

Then:

```python
from apps.epk.models import PressKit
kit = PressKit.objects.get(slug="official")
kit.set_password("choose-a-strong-password")
kit.save()
exit()
```

## Email configuration
For local development, emails print to the terminal unless SMTP credentials are set in `.env`.
For production, configure a reputable email provider (for example Brevo) and use its SMTP host, port, username and API/SMTP key. Never commit `.env`.

## Important production checklist
- Set a unique, strong `SECRET_KEY`; set `DEBUG=False`.
- Configure `ALLOWED_HOSTS` and HTTPS.
- Configure SMTP and test confirmation/unsubscribe flows.
- Add a consent-management solution before enabling non-essential analytics/marketing trackers. The included banner is a basic preference placeholder, not a full compliance certification.
- Review file upload limits, backup strategy, privacy policy and applicable data-protection requirements.
- Use a secure private media-storage strategy for confidential EPK files. A password-protected page alone does not make direct media URLs private.
- Restrict staff dashboard/admin accounts to trusted users and use strong passwords.


## Management portal (added in this version)

- Open `/dashboard/login/` for a branded staff login, then use the management dashboard at `/dashboard/`. The same full Django admin is available at `/admin/`.
- Create the first administrator with `python manage.py createsuperuser`. To create an operator account, create a staff user in Admin and grant only the model permissions they need. Operators should receive event/mix/EPK permissions only; do not grant booking, subscriber-export, user or campaign permissions unless required. A superuser can manage everything.
- Manage booking inquiries, event schedule, music links, EPK/riders/press photos, subscribers, artist profile and email campaigns through the full admin.
- Publishing a new event only sends an automatic email if `Notify subscribers` is ticked. Publishing a new mix automatically emails confirmed subscribers who opted into mix updates. Drafts do not trigger announcements. Configure SMTP in `.env` for actual delivery; without SMTP, Django prints emails in the terminal for local testing.
- Create a campaign under Email campaigns and use the campaign's Send action to send a one-off newsletter. Sent campaigns cannot be sent twice through that action.
- Event detail pages have Google Calendar and `.ics` calendar buttons.
- Run `python manage.py load_demo_data` to add clearly marked demo events, music embeds, artist profile and EPK. Replace or delete demo content before launch.
- Optional audio reference uploads are stored under `private_uploads/`, outside the public media folder and are not linked to public pages. This prevents normal public media URLs from exposing the uploaded copy; it is not DRM and a privileged server operator can still access the file. For audio that users should stream but not download, use official platform embeds rather than uploading an MP3.

### Important production notes

This is a fuller development starter, not yet a security-audited production service. Use HTTPS, a strong unique `SECRET_KEY`, `DEBUG=False`, correct `ALLOWED_HOSTS`, reliable SMTP, backups, and a production media-storage configuration. Password-protected EPK page access does not automatically make files uploaded to ordinary media fields private: configure authenticated file delivery/storage permissions before placing confidential riders or unreleased press material online. Newsletter consent and unsubscribe behavior must be reviewed against applicable privacy law before launch.
