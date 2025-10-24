# Sattler Marketplace - Design Document

## 1. Introduction

This document outlines the technical design and implementation details of the Sattler Marketplace project. The goal was to create a functional, user-friendly web application for college students to buy and sell
items, featuring core e-commerce functionalities like item listing, user messaging, and image uploads, all within a Flask-based Python environment.

## 2. Core Architecture

The application follows a standard Model-View-Controller (MVC) like pattern, facilitated by the Flask framework:

* **Model:** Represented by the SQLite database (`market.db`) and interactions handled by the CS50 SQL library. This layer manages data storage and retrieval.
* **View:** Handled by Jinja2 templates (`templates/` directory) which render HTML dynamically based on data passed from the controller. Tailwind CSS is used for styling.
* **Controller:** Implemented in `app.py`, which contains Flask route handlers. These functions process incoming HTTP requests, interact with the database (Model), and select the appropriate template (View) 
to render with the necessary context.

## 3. Key Design Decisions & Rationale

### 3.1. Database Schema (`market.db`)

SQLite was chosen for its simplicity, serverless nature, and ease of setup, making it suitable for a project of this scale. The schema is defined as follows:

* **`users` Table:**
    * Stores essential user information: `id` (PK), `username` (UNIQUE), `email` (UNIQUE), `hash` (for hashed passwords), and `created_at`.
    * Password hashing is performed using `werkzeug.security.generate_password_hash` and verified with `check_password_hash`, providing protection against direct password exposure.

* **`items` Table:**
    * Stores details of listed items: `id` (PK), `user_id` (FK to `users.id`), `title`, `description`, `price` (REAL), `category`, `image_url` (stores the *path* to the uploaded image), `status` (e.g., 'available'),
    and `listed_at`.
    * `image_url` stores a relative path like `uploads/filename.jpg`, which is then resolved using `url_for('static', filename=...)` in templates.

* **`conversations` Table:**
    * Manages chat sessions: `id` (PK), `user1_id` (FK), `user2_id` (FK), `item_id` (FK, optional, links chat to an item), `created_at`, and `updated_at`.
    * **Convention:** To ensure uniqueness and simplify lookups, `user1_id` always stores the smaller of the two participating user IDs. A `UNIQUE` constraint is placed on `(user1_id, user2_id, item_id)`.
    * `updated_at` is crucial for sorting conversations by the most recent activity. It's updated whenever a new message is added to the conversation.

* **`messages` Table:**
    * Stores individual messages: `id` (PK), `conversation_id` (FK), `sender_id` (FK), `receiver_id` (FK), `body` (TEXT), `sent_at`, and `is_read` (INTEGER, 0 or 1).
    * `is_read` flag is used for the unread message indicator feature.

* **Indexes:** Various indexes (e.g., on `users.username`, `items.user_id`, `conversations.user1_id, user2_id`, `messages.conversation_id`) are created to optimize query performance, especially for lookups, joins,
and sorting.

### 3.2. User Authentication

* **Routes:** `/register`, `/login`, `/logout`.
* **Session Management:** `Flask-Session` is configured to use the filesystem (`SESSION_TYPE = "filesystem"`). User identity (`user_id`, `username`) is stored in the session upon successful login.
* **Route Protection:** The `@login_required` decorator (from `helpers.py`) is used to restrict access to routes that require an authenticated user. It checks for `session.get("user_id")` and redirects to login 
if not found.

### 3.3. Chat System

* **Core Logic:**
    * The `get_or_create_conversation` helper function in `app.py` is central to managing conversations. It ensures that for any pair of users (and optionally an item), only one conversation record exists by 
    standardizing the order of `user1_id` and `user2_id`.
    * When a message is sent, the `updated_at` timestamp of the parent conversation is also updated.
* **Unread Messages:**
    * The `messages.is_read` flag (0 for unread, 1 for read) tracks message status.
    * When a user opens a specific chat view (`/chat/...`), messages in that conversation where they are the `receiver_id` are marked as read (`is_read = 1`).
    * A Flask context processor (`inject_global_variables`) calculates the total number of unread messages for the logged-in user across all conversations. This makes `has_unread_messages` (boolean) and
    `unread_messages_count` (integer) available to all templates, enabling the red dot indicator in `layout.html`.
* **Templating:**
    * `conversations_list.html`: Displays a list of all user's conversations, ordered by recent activity.
    * `chat_view.html`: Displays messages within a specific conversation and provides a form to send new messages. Messages are styled differently based on whether they were sent or received by the current user.

### 3.4. Frontend Design

* **Templating Engine:** Jinja2 is used for its powerful template inheritance (`{% extends "layout.html" %}`), control structures (`{% if %}`, `{% for %}`), and variable rendering (`{{ ... }}`).
* **Styling:** Tailwind CSS was chosen for its utility-first approach, allowing for rapid UI development directly within the HTML structure. This minimizes the need for custom CSS files for general layout and 
component styling.
* **Dark Mode:** Implemented using JavaScript that toggles a `.dark` class on the `<html>` element. The user's preference is stored in `localStorage`. CSS variables and Tailwind's dark mode variants (`dark:...`) 
are used to apply different styles when the dark class is present.

### 3.5. Helper Utilities (`helpers.py` and Custom Filters)

* **`apology(message, code)`:** Renders a dedicated `apology.html` template to display user-friendly error messages.
* **`login_required` Decorator:** As described in Authentication.
* **`usd(value)` Jinja Filter:** Formats numeric values as USD currency strings (e.g., `$10.50`).
* **`dateformat(value, format)` Jinja Filter:** Formats datetime strings or objects into a more readable format. This was necessary as SQLite stores timestamps as strings.

### 3.6. Error Handling and Logging

* User-facing errors are generally handled by redirecting to the `apology` page.
* Basic server-side logging (`app.logger.error()`) is implemented for critical operations like database insertion/deletion failures or file saving errors. This helps in diagnosing issues during development 
and potentially in production.

## 4. Security Considerations

* **Password Hashing:** `werkzeug.security` is used to hash passwords, preventing plain-text storage.
* **SQL Injection:** The CS50 SQL library uses parameterized queries by default, which mitigates the risk of SQL injection vulnerabilities.
* **Cross-Site Scripting (XSS):** Jinja2, by default, escapes variables rendered in templates, providing a good level of protection against XSS.
* **Access Control:** The `@login_required` decorator and explicit checks (e.g., ensuring a user can only delete their own items) are implemented to prevent unauthorized actions.

## 5. Limitations & Potential Future Improvements

* **Real-time Chat:** The current chat system requires page refreshes to see new messages. Implementing WebSockets (e.g., with Flask-SocketIO) would enable a real-time experience.
* **Search and Filtering:** No advanced search or filtering capabilities for items are currently implemented.
* **User Profiles:** Limited user profile information or public-facing profiles.
* **Item Editing:** Users cannot currently edit their listed items after posting.
* **Image Handling:** No server-side image resizing or optimization.
* **Scalability:** For a larger user base, SQLite might become a bottleneck. Migrating to a more robust database system (e.g., PostgreSQL, MySQL) would be necessary. 
* **Testing:** No automated tests (unit tests, integration tests) are included.
* **Admin Interface:** No dedicated interface for administrative tasks.

This design provides a solid foundation for the Sattler Marketplace, balancing functionality with simplicity of implementation for the given scope.
