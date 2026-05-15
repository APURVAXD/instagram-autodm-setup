# DEPLOYMENT GUIDE - Instagram AutoDM to Render

## Step-by-Step Instructions

### 1. Prepare Your Meta App

Before deploying, complete these steps in Meta Developer Console:

#### A. Create Meta Developer App
1. Go to https://developers.facebook.com/apps
2. Click "Create App" → Choose "Other" → "Business"
3. Give it a name (e.g., "Kookar AutoDM")
4. Copy your **App ID** and **App Secret** (you'll need these later)

#### B. Add Instagram Use Case
1. In left sidebar → "Use cases"
2. Click "Add use cases"
3. Add **"Manage messaging & content on Instagram"**
4. Click "Get Started" and follow prompts

#### C. Configure Products
1. In left sidebar → "Add products"
2. Add **"Facebook Login for Business"**
3. Go to Facebook Login Settings
4. Add OAuth Redirect URI: `https://YOUR-APP-NAME.onrender.com/auth/callback`
   (You'll get your Render URL in step 3, come back and update this)

#### D. Add Website Platform
1. App Settings → Basic
2. Scroll to bottom → "Add Platform" → "Website"
3. Enter: `https://YOUR-APP-NAME.onrender.com`
4. Save

### 2. Push Code to GitHub

```bash
cd instagram-autodm

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Instagram AutoDM tool"

# Create GitHub repo (go to github.com/new)
# Then connect and push:
git remote add origin https://github.com/YOUR-USERNAME/instagram-autodm.git
git branch -M main
git push -u origin main
```

### 3. Deploy to Render

#### A. Create Render Account
1. Go to https://render.com
2. Sign up (use GitHub OAuth for easy deployment)

#### B. Create New Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repo (`instagram-autodm`)
3. Give it a name (e.g., `kookar-autodm`)
4. Select:
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Free

#### C. Set Environment Variables
Before clicking "Create Web Service", add these environment variables:

```
FLASK_SECRET_KEY = <click "Generate" button>
META_APP_ID = <your Meta app ID>
META_APP_SECRET = <your Meta app secret>
BASE_URL = https://YOUR-APP-NAME.onrender.com
```

(Replace `YOUR-APP-NAME` with the name you gave in step B)

#### D. Deploy!
Click "Create Web Service" and wait ~5 minutes for first deploy.

### 4. Update Meta App with Render URL

Once deployed, Render will give you a URL like:
`https://kookar-autodm.onrender.com`

Go back to Meta Developer Console and update:

1. **Facebook Login Settings** → OAuth Redirect URI:
   ```
   https://YOUR-ACTUAL-RENDER-URL.onrender.com/auth/callback
   ```

2. **App Settings** → Basic → Website Platform:
   ```
   https://YOUR-ACTUAL-RENDER-URL.onrender.com
   ```

3. **Webhooks** (if section exists):
   - Callback URL: `https://YOUR-ACTUAL-RENDER-URL.onrender.com/webhook`
   - Verify Token: `kookar_webhook_token`
   - Subscribe to: `comments`

### 5. Configure Instagram Webhooks

1. In Meta Developer Console → Webhooks
2. Choose "Instagram" from dropdown
3. Click "Subscribe to this object"
4. Enter:
   - Callback URL: `https://YOUR-RENDER-URL.onrender.com/webhook`
   - Verify token: `kookar_webhook_token`
5. Click "Verify and Save"
6. Subscribe to `comments` field

### 6. Test Your Deployment

1. Visit your Render URL
2. Click "Connect Instagram Account"
3. Authorize your Instagram Business account
4. Configure auto-reply messages
5. Fetch recent posts
6. Enable monitoring on a post
7. Post a test comment → you should get auto-reply + DM!

---

## Keeping Render Free Tier Alive

Render free tier sleeps after 15 minutes of inactivity. To keep it alive:

### Option 1: UptimeRobot (Recommended)

1. Sign up at https://uptimerobot.com (free)
2. Add New Monitor:
   - Type: HTTP(s)
   - URL: `https://YOUR-RENDER-URL.onrender.com/`
   - Interval: 5 minutes
3. Done! Your app will never sleep.

### Option 2: Cron Job

Use a service like cron-job.org to ping your app every 10 minutes.

---

## Troubleshooting

### "Authorization failed" during Instagram login
- Check OAuth Redirect URI matches exactly (including https)
- Make sure your Instagram account is Business or Creator
- Verify Instagram is connected to a Facebook Page

### "No Instagram Business Account found"
- Go to Instagram app → Profile → Edit Profile → Page
- Connect to a Facebook Page
- Try authorization again

### Webhook not receiving events
- Check webhook URL is correct in Meta Developer Console
- Verify token must be exactly: `kookar_webhook_token`
- Subscribe to `comments` field
- Test by commenting on a monitored post

### DMs not sending
- Ensure Instagram Business Account is properly connected
- Check access token hasn't expired (should be 60-day long-lived)
- Verify "Manage messaging" permission was granted during OAuth

### Database errors
- Render creates a persistent disk for SQLite
- If you redeploy, database persists
- To reset: delete and recreate the web service

---

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `FLASK_SECRET_KEY` | Flask session encryption key | Auto-generated by Render |
| `META_APP_ID` | Your Meta app ID | `1234567890` |
| `META_APP_SECRET` | Your Meta app secret | `abc123...` |
| `BASE_URL` | Your Render deployment URL | `https://kookar-autodm.onrender.com` |

---

## Updating Your App

To deploy updates:

```bash
# Make changes to code
git add .
git commit -m "Update: describe changes"
git push origin main
```

Render will automatically detect the push and redeploy (~3-5 minutes).

---

## Security Best Practices

✅ **Do:**
- Use strong Meta app secret
- Keep environment variables private
- Use HTTPS only (Render provides this)
- Regularly check Meta Developer Console for security alerts

❌ **Don't:**
- Commit `.env` files to GitHub
- Share your Meta app credentials
- Use the same app for multiple services
- Expose your Render dashboard URL

---

## Cost Breakdown

**Render Free Tier:**
- 750 hours/month (always-on with UptimeRobot)
- Sleeps after 15 min inactivity
- 100 GB bandwidth/month
- Persistent disk for SQLite

**Fully Free Setup:**
- Render (web hosting): $0
- UptimeRobot (keep-alive): $0
- Meta Developer (API): $0
- **Total: $0/month**

**Optional Paid Upgrades:**
- Render Starter ($7/month): No sleep, faster deployment
- Render Standard ($25/month): Custom domain, more resources

---

## Next Steps

After successful deployment:

1. **Add all your Instagram accounts** (unlimited supported)
2. **Configure custom messages** per account
3. **Enable monitoring** on high-engagement posts
4. **Track results** in the dashboard
5. **Scale!** Share the tool with team members

---

## Support

If you encounter issues:

1. Check Render logs: Dashboard → Logs tab
2. Review Meta Developer Console → Webhooks → Test
3. Verify all environment variables are set correctly
4. Check Instagram account has all required permissions

---

**You're done! Your Instagram AutoDM tool is now live.** 🎉

Visit: `https://YOUR-RENDER-URL.onrender.com` and start automating!
