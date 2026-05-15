# Instagram AutoDM Tool
Multi-account Instagram comment auto-responder with DM automation

## Prerequisites Checklist

Before deploying, ensure you have:

### Instagram Setup
- [ ] Account converted to Business or Creator
- [ ] Instagram linked to a Facebook Page
- [ ] Meta Developer App created
- [ ] "Manage messaging & content on Instagram" use case added
- [ ] Facebook Login for Business product added
- [ ] OAuth redirect URI configured: `https://YOUR-APP.onrender.com/auth/callback`
- [ ] Website platform added: `https://YOUR-APP.onrender.com`

### Meta App Credentials
- [ ] App ID copied
- [ ] App Secret copied
- [ ] Instagram Business Account ID obtained

### Deployment
- [ ] Render.com account created
- [ ] Environment variables ready to set

---

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_SECRET_KEY="your-random-secret-key"
export META_APP_ID="your-app-id"
export META_APP_SECRET="your-app-secret"
export BASE_URL="http://localhost:5000"

# Run locally
python app.py
```

Visit http://localhost:5000

---

## Deploy to Render

1. Push this code to GitHub
2. Create new Web Service on Render
3. Connect your GitHub repo
4. Set environment variables in Render dashboard
5. Deploy!

---

## Environment Variables (set in Render)

```
FLASK_SECRET_KEY=<generate-random-string>
META_APP_ID=<your-meta-app-id>
META_APP_SECRET=<your-meta-app-secret>
BASE_URL=https://your-app.onrender.com
```

---

## Usage

1. Visit your deployed app URL
2. Click "Connect Instagram Account"
3. Authorize via Meta
4. Configure auto-reply message
5. Select posts to enable auto-DM
6. Comments will now trigger automatic replies + DMs!

---

## Features

✅ Multi-account support (unlimited Instagram accounts)
✅ Custom reply messages per account
✅ Custom DM messages per account
✅ Select specific posts to trigger on
✅ Dashboard to manage everything
✅ CTA buttons in DMs (optional)
✅ Comment history tracking
✅ Free hosting on Render
✅ Automatic webhook subscription

---

## Tech Stack

- Python 3.11
- Flask (web framework)
- SQLite (database)
- Instagram Graph API
- Gunicorn (production server)
- Render.com (hosting)

---

## File Structure

```
instagram-autodm/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── instagram_api.py       # Instagram API wrapper
├── requirements.txt       # Python dependencies
├── runtime.txt           # Python version
├── render.yaml           # Render configuration
├── templates/
│   ├── index.html        # Dashboard
│   └── login.html        # Login page
└── static/
    └── style.css         # Styling
```

---

## Support

For issues or questions, check:
- Instagram Graph API docs: https://developers.facebook.com/docs/instagram-api
- Meta for Developers: https://developers.facebook.com
