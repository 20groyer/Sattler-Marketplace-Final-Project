import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timezone

from helpers import apology, login_required, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# --- Custom Jinja2 Filters ---
@app.template_filter('dateformat')
def format_datetime_filter(value, format='%Y-%m-%d %H:%M'):
    """Custom Jinja filter to format a datetime string or object."""
    if value is None: return ""
    if isinstance(value, str):
        try:
            dt_obj = datetime.fromisoformat(value.replace('Z', '+00:00')) if 'T' in value else datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try: dt_obj = datetime.strptime(value, '%Y-%m-%d')
            except ValueError: return value
    elif isinstance(value, datetime): dt_obj = value
    else: return value
    if dt_obj.tzinfo is None: dt_obj = dt_obj.replace(tzinfo=timezone.utc)
    return dt_obj.strftime(format)

app.jinja_env.filters["usd"] = usd
# --- End Custom Jinja2 Filters ---

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///market.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.context_processor
def inject_global_variables():
    """Injects global variables into all templates."""
    unread_messages_count = 0
    if "user_id" in session:
        count_result = db.execute(
            "SELECT COUNT(id) as unread_count FROM messages WHERE receiver_id = ? AND is_read = 0",
            session["user_id"]
        )
        if count_result and count_result[0]["unread_count"] > 0:
            unread_messages_count = count_result[0]["unread_count"]

    return {
        'now': datetime.now(timezone.utc),
        'has_unread_messages': unread_messages_count > 0,
        'unread_messages_count': unread_messages_count # Optional: if you want to display the count
    }


# --- Standard Routes (Home, Auth, Items) ---
@app.route("/")
@login_required
def index():
    """Show all available items, excluding the user's own items."""
    items = db.execute("""
        SELECT items.*, users.username AS seller_username
        FROM items
        JOIN users ON items.user_id = users.id
        WHERE items.status = 'available' AND items.user_id != ?
        ORDER BY items.listed_at DESC
    """, session["user_id"])
    return render_template("index.html", items=items)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username: return apology("must provide username", 400)
        if not email: return apology("must provide email", 400)
        if not password: return apology("must provide password", 400)
        if password != confirmation: return apology("passwords do not match", 400)

        rows = db.execute("SELECT * FROM users WHERE username = ? OR email = ?", username, email)
        if len(rows) > 0:
            if rows[0]["username"] == username: return apology("username already taken", 400)
            if rows[0]["email"] == email: return apology("email already registered", 400)

        hash_password = generate_password_hash(password)
        try:
            user_id = db.execute("INSERT INTO users (username, email, hash) VALUES (?, ?, ?)",
                                 username, email, hash_password)
        except Exception as e:
            app.logger.error(f"Error inserting user: {e}")
            return apology("registration failed, please try again", 500)

        session["user_id"] = user_id
        session["username"] = username
        flash("Registered successfully!", "success")
        return redirect(url_for("index"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username: return apology("must provide username", 403)
        if not password: return apology("must provide password", 403)
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("invalid username and/or password", 403)
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]
        flash(f"Welcome back, {session['username']}!", "success")
        return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell an item"""
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        price_str = request.form.get("price")
        category = request.form.get("category")
        image_url = request.form.get("image_url")

        if not title: return apology("must provide title", 400)
        if not description: return apology("must provide description", 400)
        if not price_str: return apology("must provide price", 400)
        try:
            price = float(price_str)
            if price <= 0: return apology("price must be positive", 400)
        except ValueError: return apology("invalid price format", 400)
        if not category: category = "Other"

        try:
            db.execute("INSERT INTO items (user_id, title, description, price, category, image_url) VALUES (?, ?, ?, ?, ?, ?)",
                       session["user_id"], title, description, price, category, image_url)
        except Exception as e:
            app.logger.error(f"Error inserting item: {e}")
            return apology("failed to list item", 500)
        flash("Item listed successfully!", "success")
        return redirect(url_for("index"))
    return render_template("sell.html")


@app.route("/history")
@login_required
def history():
    """Show history of items listed by the user"""
    items = db.execute("SELECT * FROM items WHERE user_id = ? ORDER BY listed_at DESC", session["user_id"])
    return render_template("history.html", items=items)


@app.route("/delete_item/<int:item_id>", methods=["POST"])
@login_required
def delete_item(item_id):
    """Delete a listed item if it belongs to the current user."""
    item_owner = db.execute("SELECT user_id FROM items WHERE id = ?", item_id)
    if not item_owner or item_owner[0]["user_id"] != session["user_id"]:
        flash("Item not found or you don't have permission to delete it.", "error")
        return redirect(url_for("history"))
    try:
        db.execute("DELETE FROM items WHERE id = ?", item_id)
        flash("Item deleted successfully!", "success")
    except Exception as e:
        app.logger.error(f"Error deleting item {item_id}: {e}")
        flash("Failed to delete item.", "error")
    return redirect(url_for("history"))

# --- Chat Helper Function ---
def get_or_create_conversation(user1_id, user2_id, item_id=None):
    """Gets an existing conversation or creates a new one. Ensures user1_id < user2_id."""
    if user1_id == user2_id: return None
    if user1_id > user2_id: user1_id, user2_id = user2_id, user1_id

    query = "SELECT id FROM conversations WHERE user1_id = ? AND user2_id = ? AND "
    params = [user1_id, user2_id]
    if item_id:
        query += "item_id = ?"
        params.append(item_id)
    else:
        query += "item_id IS NULL"

    conversation_rows = db.execute(query, *params)

    if conversation_rows:
        return conversation_rows[0]["id"]
    else:
        try:
            current_time = datetime.now(timezone.utc)
            new_conversation_id = db.execute(
                "INSERT INTO conversations (user1_id, user2_id, item_id, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                user1_id, user2_id, item_id, current_time, current_time
            )
            return new_conversation_id
        except Exception as e:
            app.logger.error(f"Error creating/fetching conversation between {user1_id} and {user2_id} for item {item_id}: {e}")
            # Re-fetch in case of race condition where another process created it.
            conversation_rows = db.execute(query, *params)
            if conversation_rows: return conversation_rows[0]["id"]
            return None

# --- Chat Routes ---
@app.route("/messages")
@login_required
def list_conversations():
    """List all conversations for the current user."""
    user_id = session["user_id"]
    conversations = db.execute("""
        SELECT
            c.id AS conversation_id, c.item_id, c.updated_at,
            CASE WHEN c.user1_id = :uid THEN u2.username ELSE u1.username END AS other_user_username,
            CASE WHEN c.user1_id = :uid THEN c.user2_id ELSE c.user1_id END AS other_user_id,
            i.title AS item_title,
            (SELECT m.body FROM messages m WHERE m.conversation_id = c.id ORDER BY m.sent_at DESC LIMIT 1) AS last_message_body,
            (SELECT m.sent_at FROM messages m WHERE m.conversation_id = c.id ORDER BY m.sent_at DESC LIMIT 1) AS last_message_time,
            (SELECT COUNT(m.id) FROM messages m WHERE m.conversation_id = c.id AND m.receiver_id = :uid AND m.is_read = 0) AS unread_in_conv_count
        FROM conversations c
        JOIN users u1 ON c.user1_id = u1.id
        JOIN users u2 ON c.user2_id = u2.id
        LEFT JOIN items i ON c.item_id = i.id
        WHERE c.user1_id = :uid OR c.user2_id = :uid
        ORDER BY c.updated_at DESC
    """, uid=user_id)
    return render_template("conversations_list.html", conversations=conversations)

@app.route("/chat/<int:other_user_id>", methods=["GET", "POST"])
@app.route("/chat/<int:other_user_id>/item/<int:item_id>", methods=["GET", "POST"])
@login_required
def chat_view(other_user_id, item_id=None):
    """Display chat, mark messages as read, and handle sending new messages."""
    current_user_id = session["user_id"]

    if current_user_id == other_user_id:
        flash("You cannot start a conversation with yourself.", "error")
        return redirect(url_for("list_conversations"))

    other_user_details = db.execute("SELECT username FROM users WHERE id = ?", other_user_id)
    if not other_user_details: return apology("User not found", 404)
    other_user_username = other_user_details[0]["username"]

    conversation_id = get_or_create_conversation(current_user_id, other_user_id, item_id)
    if not conversation_id:
        flash("Could not start or find conversation.", "error")
        return redirect(request.referrer or url_for("index"))

    if request.method == "POST":
        message_body = request.form.get("message_body")
        if not message_body or not message_body.strip():
            flash("Message cannot be empty.", "warning")
        else:
            try:
                db.execute(
                    "INSERT INTO messages (conversation_id, sender_id, receiver_id, body) VALUES (?, ?, ?, ?)",
                    conversation_id, current_user_id, other_user_id, message_body.strip()
                )
                db.execute(
                    "UPDATE conversations SET updated_at = ? WHERE id = ?",
                    datetime.now(timezone.utc), conversation_id
                )
                # Redirect to clear form and show new message
                redirect_url = url_for("chat_view", other_user_id=other_user_id, item_id=item_id) if item_id else url_for("chat_view", other_user_id=other_user_id)
                return redirect(redirect_url)
            except Exception as e:
                app.logger.error(f"Error sending message in conv {conversation_id}: {e}")
                flash("Error sending message.", "error")

    # Mark messages in this conversation as read for the current user
    db.execute(
        "UPDATE messages SET is_read = 1 WHERE conversation_id = ? AND receiver_id = ? AND is_read = 0",
        conversation_id, current_user_id
    )

    messages = db.execute("""
        SELECT m.*, u.username as sender_username
        FROM messages m JOIN users u ON m.sender_id = u.id
        WHERE m.conversation_id = ? ORDER BY m.sent_at ASC
    """, conversation_id)

    item_info = None
    if item_id:
        item_info_rows = db.execute("SELECT title FROM items WHERE id = ?", item_id)
        if item_info_rows: item_info = item_info_rows[0]

    return render_template("chat_view.html", messages=messages, conversation_id=conversation_id,
                           other_user_id=other_user_id, other_user_username=other_user_username,
                           item_id=item_id, item_details=item_info)


if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.run(debug=True)
