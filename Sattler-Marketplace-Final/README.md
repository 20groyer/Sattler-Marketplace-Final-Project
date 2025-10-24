# Sattler Marketplace “SattlerMarket”

## 1. 👋 Introduction: Welcome!
    * **What is this project?** So this project is our mini Amazon! Though slightly less robust. Sattler Marketplace is a web application inspired by and dedicated to the Sattler College community, allowing its users to post items, browse posted items, and even message sellers!

    * **What's its main goal or purpose?** It’s designed for students and staff to easily sell as well as buy stuff and to communicate between users within the website.

## 2. ✨ Features at a Glance
    * Provide a bulleted list of the main things users can do. Be concise but cover all key functionalities.
        * User Registration & Login - Users can register for an account. Once they register, they can use their credentials to log in and begin to use the web application.
        * Item Browsing - Users can see the listed items available.
        * Listing New Items for Sale (with image uploads!) - Users can navigate to the “Sell item” tab on the nav bar and fill out the details for their desired item and list the item.
        * Managing "My Listings" (viewing, deleting) - Users can navigate to the “My Listings” tab using the nav bar and manage their posted items, either by viewing or deleting them.
        * User-to-User Chat/Messaging - Users can view posted items and easily navigate and message the seller of the item by clicking the “Home” button
        * Unread Message Notifications - Users will be notified of unread messages via a red dot on the messages tab in the navigation bar.
        * Dark Mode Toggle - users can switch from light to dark mode by clicking on the moon icon in the top right corner of the screen, and vice versa.


## 3. 🛠️ Tech Stack (What's it Made Of?)
        * Backend: Python (Flask)
        * Database: SQLite (using CS50 Library)
        * Frontend: HTML, Tailwind CSS, Jinja2
        * Session Management: Flask-Session.
        * Password Security: Werkzeug for secure password hashing

## 4. ⚙️ Getting Started: Setup & Configuration (Let's Get it Running!)
    * This section is CRUCIAL for your instructors. Be extremely clear and step-by-step.
    * **A. Prerequisites:** - A functioning web browser, such as Chrome, will need to be installed on your device. The latest version is preferred.
    * **B. Step-by-Step Installation:**
**Get the Code:** Download the zipped code file and then run the command “unzip sattlermarket.zip” in your terminal
Change directory - run “cd sattlermarket”
Run Flask - start the web application by running the following command: “flask run”
Go to the website - you will see a pop-up window and press the “open in browser” button.

    * **C. Expected Outcome: You should now see the Sattler Marketplace homepage.

## 5. 📖 How to Use Sattler Marketplace: A Walkthrough
* **A. Registering an Account:**
To register for an account, you will begin at the website's login landing page. Navigate to the nav bar on the top right margin of the page and click on the “registration” button. It will take you to a page that will prompt you to fill in your registration information.
* ** What to fill in. - Fill in all the information requested, including your email address, username, and passwords.
* ** What happens upon success. - Once completed, you can submit the form by clicking on the “submit” button, and you should be redirected to the home page with a green “registered successfully” prompt displayed!
    * **B. Logging In & Out:** - To log out successfully, simply click on the “log out” button found at the top right of your screen on the navigation bar. And to log in, simply fill out your username and password details.
    * **C. Browsing Items:** - When browsing items, you will see the image of the item listed along with a short description, its price, category, date posted, as well as the name of the seller.
    * **D. Listing an Item for Sale:** - To sell an item simply navigate to the sell item tab by clicking on the “sell item” button on the top right of the screen, on the navigation bar.
The details of the “Sell item” form include the following: title of your item; description of you item; price (in dollars) of your item; a category; and image URL.
    * **E. Managing "My Listings":** - Once you post an item it is then added to your listings. To navigate to this tab and view your listings, you can simply click on the “My Listings” button found at the top right of your screen on the navigation bar.
The information listed on the “My listings” page is the set of items you have uploaded to your account/website.
        * **How to delete an item:** Explain the button and confirmation. What happens to the image file?
To delete an item from your listings, simply click on the delete button in the “actions” column and click “confirm” when prompted.
    * **F. Messaging & Chat:**
        * **Starting a chat:** If you want to start a conversation with the dealer, press the “Message Seller” button on the listing displayed in the /index (Home).
        * **The "Messages" Page:** To view messages, you can click on the “Messages” button on the navigation bar.
        * **Unread Message Indicator:** Red dot above the “Messages” button indicates that you have an unread message!
        * **Chat View:** If you want to read or go back to previously opened chats, just click on the  “Messages” button and then click on the chat you would like to view.
        * **Marking messages as read:** If you go into a conversation where you have an unread message, it will be automatically marked as read.
    * **G. Using Dark Mode:**
        * Dark mode can be toggled with the sun icon in the top right corner of your screen, and vice versa for light mode.

## 6. 🤔 Troubleshooting & FAQs
* **Image Uploads Not Working?** Check if the image URL is correct
* **"Why don't I see my own items on the homepage?"** You are not supposed to see your own items on the home page. If you want to check them go to /history (My Listings)
* **Debug Mode:** debug=True is active. In a production scenario, this would be set to `False` for security and performance.

## 7. 👋 A Final Note
    * We believe this documentation provides a clear path for testing all implemented features. Thank you for your time and evaluation.


Explanation video link: https://youtu.be/7jh6JL3C3-8
