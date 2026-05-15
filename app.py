from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import secrets
import requests
from instagram_api import InstagramAPI
from models import Account, MonitoredPost, ProcessedComment

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(32))

# Meta app credentials
META_APP_ID = os.environ.get('META_APP_ID')
META_APP_SECRET = os.environ.get('META_APP_SECRET')
BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')

# OAuth URLs
AUTH_URL = "https://www.facebook.com/v19.0/dialog/oauth"
TOKEN_URL = "https://graph.facebook.com/v19.0/oauth/access_token"

@app.route('/')
def index():
    """Dashboard - show all connected accounts"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    accounts = Account.get_all()
    return render_template('index.html', accounts=accounts)

@app.route('/login')
def login():
    """Login page"""
    return render_template('login.html')

@app.route('/auth/instagram')
def auth_instagram():
    """Initiate Instagram OAuth flow"""
    scope = 'instagram_basic,instagram_manage_comments,pages_show_list,pages_read_engagement'
    redirect_uri = f"{BASE_URL}/auth/callback"
    
    auth_url = (
        f"{AUTH_URL}?"
        f"client_id={META_APP_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scope}&"
        f"response_type=code&"
        f"state={secrets.token_urlsafe(32)}"
    )
    
    return redirect(auth_url)

@app.route('/auth/callback')
def auth_callback():
    """Handle OAuth callback"""
    code = request.args.get('code')
    if not code:
        return "Authorization failed", 400
    
    # Exchange code for access token
    redirect_uri = f"{BASE_URL}/auth/callback"
    token_response = requests.get(TOKEN_URL, params={
        'client_id': META_APP_ID,
        'client_secret': META_APP_SECRET,
        'redirect_uri': redirect_uri,
        'code': code
    })
    
    response_data = token_response.json()
    print(f"Meta token response: {response_data}")
    
    short_lived_token = response_data.get('access_token')
    if not short_lived_token:
        error_msg = response_data.get('error', {})
        print(f"Token exchange failed: {error_msg}")
        return f"Failed to get access token: {error_msg.get('message', 'Unknown error')}", 400
    
    # Exchange for long-lived token
    access_token = InstagramAPI.get_long_lived_token(
        short_lived_token, META_APP_ID, META_APP_SECRET
    )
    
    # Get user's Facebook pages
    api = InstagramAPI(access_token)
    pages = InstagramAPI.get_user_pages(access_token)
    
    if not pages:
        return "No Facebook Pages found. Please connect Instagram to a Facebook Page first.", 400
    
    # Get first page (user can select different one later if needed)
    page_id = pages[0]['id']
    
    # Get Instagram Business Account ID
    instagram_user_id = api.get_instagram_business_account(page_id)
    
    if not instagram_user_id:
        return "No Instagram Business Account found on this Page. Please connect Instagram to your Facebook Page.", 400
    
    # Get Instagram username
    user_info = api.get_user_info()
    username = user_info.get('username', 'Unknown')
    
    # Save account to database
    account_id = Account.create(instagram_user_id, username, access_token, page_id)
    
    # Subscribe to webhooks
    api.subscribe_to_webhooks(instagram_user_id)
    
    # Set session
    session['user_id'] = account_id
    session['instagram_user_id'] = instagram_user_id
    
    return redirect(url_for('index'))

@app.route('/account/<int:account_id>')
def account_detail(account_id):
    """Account detail page"""
    account = Account.get_by_id(account_id)
    if not account:
        return "Account not found", 404
    
    # Get monitored posts
    monitored_posts = MonitoredPost.get_by_account(account_id)
    
    # Get recent comments processed
    recent_comments = ProcessedComment.get_by_account(account_id, limit=20)
    
    return render_template('account_detail.html', 
                         account=account, 
                         monitored_posts=monitored_posts,
                         recent_comments=recent_comments)

@app.route('/account/<int:account_id>/settings', methods=['POST'])
def update_account_settings(account_id):
    """Update account reply/DM messages"""
    reply_message = request.form.get('reply_message')
    dm_message = request.form.get('dm_message')
    cta_button_text = request.form.get('cta_button_text')
    cta_button_url = request.form.get('cta_button_url')
    
    Account.update_messages(account_id, reply_message, dm_message, cta_button_text, cta_button_url)
    
    return redirect(url_for('account_detail', account_id=account_id))

@app.route('/account/<int:account_id>/fetch-posts', methods=['POST'])
def fetch_posts(account_id):
    """Fetch recent posts from Instagram"""
    account = Account.get_by_id(account_id)
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    
    api = InstagramAPI(account['access_token'])
    media = api.get_recent_media(account['instagram_user_id'], limit=20)
    
    # Add posts to database
    for post in media:
        MonitoredPost.add(
            account_id,
            post['id'],
            post.get('caption', '')[:200]  # Truncate caption
        )
    
    return jsonify({'success': True, 'count': len(media)})

@app.route('/post/<int:post_id>/toggle', methods=['POST'])
def toggle_post(post_id):
    """Enable/disable monitoring for a post"""
    enabled = request.json.get('enabled', True)
    MonitoredPost.toggle_enabled(post_id, enabled)
    return jsonify({'success': True})

@app.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    """Remove post from monitoring"""
    MonitoredPost.delete(post_id)
    return jsonify({'success': True})

@app.route('/account/<int:account_id>/delete', methods=['POST'])
def delete_account(account_id):
    """Disconnect account"""
    Account.delete(account_id)
    return redirect(url_for('index'))

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """Instagram webhook endpoint"""
    
    if request.method == 'GET':
        # Webhook verification
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        # Verify token (you can set this to any string)
        if mode == 'subscribe' and token == 'kookar_webhook_token':
            return challenge, 200
        return 'Verification failed', 403
    
    # Handle webhook event (POST)
    data = request.json
    
    if not data:
        return 'No data', 400
    
    # Process Instagram comment events
    if data.get('object') == 'instagram':
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                if change.get('field') == 'comments':
                    value = change.get('value', {})
                    
                    # Extract comment data
                    comment_id = value.get('id')
                    media_id = value.get('media', {}).get('id')
                    commenter_id = value.get('from', {}).get('id')
                    commenter_username = value.get('from', {}).get('username')
                    comment_text = value.get('text', '')
                    
                    # Process comment
                    process_comment(comment_id, media_id, commenter_id, commenter_username, comment_text)
    
    return 'OK', 200

def process_comment(comment_id, media_id, commenter_id, commenter_username, comment_text):
    """Process new comment: reply only (DM functionality disabled)"""
    
    # Check if already processed
    if ProcessedComment.is_processed(comment_id):
        return
    
    # Find account that owns this post
    # (We need to match media_id to our monitored_posts)
    import sqlite3
    conn = sqlite3.connect('autodm.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT mp.*, a.* 
        FROM monitored_posts mp
        JOIN accounts a ON mp.account_id = a.id
        WHERE mp.post_id = ? AND mp.enabled = 1
    ''', (media_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        # Post not monitored
        return
    
    account = dict(result)
    api = InstagramAPI(account['access_token'])
    
    # Reply to comment
    try:
        api.reply_to_comment(comment_id, account['reply_message'])
    except Exception as e:
        print(f"Failed to reply to comment: {e}")
    
    # Send DM
    dm_sent = False
# try:
#     api.send_dm(
#         account['instagram_user_id'],
#         commenter_id,
#         account['dm_message'],
#         account.get('cta_button_text'),
#         account.get('cta_button_url')
#     )
#     dm_sent = True
# except Exception as e:
#     print(f"Failed to send DM: {e}")
    
    # Mark as processed
    ProcessedComment.add(
        comment_id,
        account['id'],
        media_id,
        commenter_id,
        commenter_username,
        comment_text,
        dm_sent
    )

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
