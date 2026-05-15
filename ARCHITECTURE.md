# Instagram AutoDM - Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    INSTAGRAM AUTODM SYSTEM                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         USER FLOW                                │
└─────────────────────────────────────────────────────────────────┘

1. Connect Account
   User → Login Page → Meta OAuth → Callback → Save to DB

2. Configure
   User → Account Settings → Set Messages → Enable Posts

3. Auto-Respond
   Comment → Webhook → Process → Reply + DM → Save to DB


┌─────────────────────────────────────────────────────────────────┐
│                      SYSTEM ARCHITECTURE                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐          ┌──────────────┐          ┌──────────────┐
│   Instagram  │◄────────►│  Your App    │◄────────►│   SQLite DB  │
│   Graph API  │  OAuth   │  (Render)    │  Store   │  autodm.db   │
└──────────────┘          └──────────────┘          └──────────────┘
       ▲                         ▲
       │                         │
       │ Webhook                 │ HTTP
       │ (Comments)              │
       │                         │
   ┌───┴──────┐            ┌────┴─────┐
   │Instagram │            │  User    │
   │ Comments │            │ Browser  │
   └──────────┘            └──────────┘


┌─────────────────────────────────────────────────────────────────┐
│                         FILE STRUCTURE                           │
└─────────────────────────────────────────────────────────────────┘

instagram-autodm/
│
├── 🐍 BACKEND (Python/Flask)
│   ├── app.py                  # Main application (routes, logic)
│   ├── models.py               # Database models (SQLite)
│   └── instagram_api.py        # API wrapper (Graph API calls)
│
├── 🎨 FRONTEND (HTML/CSS)
│   └── templates/
│       ├── login.html          # OAuth login page
│       ├── index.html          # Dashboard (accounts list)
│       └── account_detail.html # Account management page
│
├── ⚙️ CONFIGURATION
│   ├── requirements.txt        # Python dependencies
│   ├── runtime.txt             # Python version
│   ├── render.yaml             # Render deployment config
│   ├── .env.example            # Environment template
│   └── .gitignore              # Git ignore rules
│
└── 📚 DOCUMENTATION
    ├── README.md               # Quick overview
    ├── DEPLOYMENT.md           # Step-by-step deployment
    ├── PROJECT_SUMMARY.md      # Complete guide
    └── ARCHITECTURE.md         # This file


┌─────────────────────────────────────────────────────────────────┐
│                        DATA FLOW                                 │
└─────────────────────────────────────────────────────────────────┘

[User Comments on Post]
         ↓
[Instagram sends webhook]
         ↓
[Render receives POST /webhook]
         ↓
[Check if post is monitored]
         ↓
[Check if comment already processed]
         ↓
┌────────────────────────┐
│   Process Comment:     │
│   1. Reply to comment  │
│   2. Send DM           │
│   3. Save to database  │
└────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                      DATABASE SCHEMA                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐
│       accounts          │  ← Connected Instagram accounts
├─────────────────────────┤
│ id                      │
│ instagram_user_id       │
│ username                │
│ access_token            │
│ page_id                 │
│ reply_message           │
│ dm_message              │
│ cta_button_text         │
│ cta_button_url          │
│ created_at              │
└─────────────────────────┘
         │
         │ 1:N
         ↓
┌─────────────────────────┐
│    monitored_posts      │  ← Posts to watch for comments
├─────────────────────────┤
│ id                      │
│ account_id              │ (FK → accounts.id)
│ post_id                 │
│ post_caption            │
│ enabled                 │
│ created_at              │
└─────────────────────────┘
         │
         │ 1:N
         ↓
┌─────────────────────────┐
│   processed_comments    │  ← Comment history
├─────────────────────────┤
│ id                      │
│ comment_id              │
│ account_id              │ (FK → accounts.id)
│ post_id                 │
│ commenter_id            │
│ commenter_username      │
│ comment_text            │
│ replied_at              │
│ dm_sent                 │
└─────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                        API ENDPOINTS                             │
└─────────────────────────────────────────────────────────────────┘

PUBLIC ROUTES:
GET  /                          # Dashboard
GET  /login                     # Login page
GET  /logout                    # Logout

OAUTH ROUTES:
GET  /auth/instagram            # Initiate OAuth flow
GET  /auth/callback             # OAuth callback

ACCOUNT ROUTES:
GET  /account/<id>              # Account detail page
POST /account/<id>/settings     # Update messages
POST /account/<id>/fetch-posts  # Fetch recent posts
POST /account/<id>/delete       # Disconnect account

POST ROUTES:
POST /post/<id>/toggle          # Enable/disable monitoring
POST /post/<id>/delete          # Remove from monitoring

WEBHOOK ROUTES:
GET  /webhook                   # Webhook verification
POST /webhook                   # Receive Instagram events


┌─────────────────────────────────────────────────────────────────┐
│                    INSTAGRAM API CALLS                           │
└─────────────────────────────────────────────────────────────────┘

AUTHENTICATION:
GET /oauth/access_token         # Exchange code for token
GET /oauth/access_token         # Get long-lived token (60 days)

USER INFO:
GET /me                         # Get Instagram user profile
GET /me/accounts                # Get connected Facebook Pages
GET /{page-id}                  # Get Instagram Business Account ID

MEDIA:
GET /{instagram-user-id}/media  # Get recent posts
GET /{media-id}/comments        # Get comments on post

INTERACTIONS:
POST /{comment-id}/replies      # Reply to comment
POST /{instagram-user-id}/messages  # Send DM

WEBHOOKS:
POST /{instagram-user-id}/subscribed_apps  # Subscribe to events


┌─────────────────────────────────────────────────────────────────┐
│                   DEPLOYMENT ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│                          RENDER.COM                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Web Service (Free Tier)                                 │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  Gunicorn + Flask App                              │  │  │
│  │  │  ┌──────────────────────────────────────────────┐  │  │  │
│  │  │  │  app.py (routes, logic)                      │  │  │  │
│  │  │  │  models.py (database)                        │  │  │  │
│  │  │  │  instagram_api.py (API calls)                │  │  │  │
│  │  │  └──────────────────────────────────────────────┘  │  │  │
│  │  │  ┌──────────────────────────────────────────────┐  │  │  │
│  │  │  │  SQLite Database (autodm.db)                 │  │  │  │
│  │  │  │  - Persistent disk                           │  │  │  │
│  │  │  └──────────────────────────────────────────────┘  │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ▲                                     │
│                           │ HTTPS                               │
└───────────────────────────┼─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────┴─────┐      ┌──────┴──────┐    ┌──────┴──────┐
   │Instagram │      │   Users     │    │ UptimeRobot │
   │ Webhooks │      │  (Browser)  │    │ (Keep-Alive)│
   └──────────┘      └─────────────┘    └─────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                             │
└─────────────────────────────────────────────────────────────────┘

1. OAuth 2.0
   ✓ Secure Instagram authorization
   ✓ No password handling
   ✓ Long-lived tokens (60 days)

2. HTTPS
   ✓ All traffic encrypted
   ✓ Enforced by Render

3. Session Management
   ✓ Flask sessions encrypted
   ✓ Secret key in environment

4. Webhook Verification
   ✓ Verify token check
   ✓ Signature validation

5. Environment Variables
   ✓ No secrets in code
   ✓ Render secure storage

6. Database
   ✓ File-based SQLite
   ✓ Persistent disk
   ✓ No external access


┌─────────────────────────────────────────────────────────────────┐
│                     SCALING STRATEGY                             │
└─────────────────────────────────────────────────────────────────┘

FREE TIER (Current):
- Render free tier (750 hrs/month)
- SQLite database
- UptimeRobot keep-alive
- Handles: 100+ accounts, 10K+ comments/day

STARTER ($7/month):
- Render Starter plan
- Always-on (no sleep)
- Faster deployment
- Same SQLite DB

SCALE ($25/month):
- Render Standard plan
- PostgreSQL database
- Redis caching
- Custom domain
- Handles: 1000+ accounts, 1M+ comments/day

ENTERPRISE:
- Multiple Render instances
- PostgreSQL cluster
- Redis cluster
- CDN for static assets
- Load balancing
- Job queue (Celery)


┌─────────────────────────────────────────────────────────────────┐
│                    MONITORING & ALERTS                           │
└─────────────────────────────────────────────────────────────────┘

Built-in:
✓ Render logs (Dashboard → Logs)
✓ Meta Developer Console webhooks test
✓ Database query logs

Optional (Free):
✓ UptimeRobot uptime monitoring
✓ Render metrics (response time, memory)
✓ Meta app insights

Optional (Paid):
- Sentry error tracking
- LogRocket session replay
- Mixpanel analytics


┌─────────────────────────────────────────────────────────────────┐
│                        SUCCESS METRICS                           │
└─────────────────────────────────────────────────────────────────┘

Engagement:
- Comments processed / day
- DMs sent successfully
- Reply success rate

Growth:
- Accounts connected
- Posts monitored
- Active users

Performance:
- Webhook response time (<1s ideal)
- DM send time (<3s ideal)
- Database query time (<100ms ideal)

Business:
- Comments → Signups conversion rate
- CTA button click-through rate
- Customer acquisition cost


┌─────────────────────────────────────────────────────────────────┐
│                      NEXT STEPS                                  │
└─────────────────────────────────────────────────────────────────┘

1. Setup Meta Developer App (5 min)
2. Push code to GitHub (2 min)
3. Deploy to Render (5 min)
4. Configure webhooks (2 min)
5. Setup UptimeRobot (2 min)
6. Test with your account (5 min)
7. Go live! 🚀

Total time: ~20 minutes from zero to production
```
