News Application

Overview

This is a Django-based web application that supports user management, content creation and publishing, and subscriptions configured to use a MySQL database. The project includes Sphinx documentation and containerisation using Docker.

Running the Application Locally (venv setup)

1. Clone the Repository

git clone <https://github.com/Slindo-M/news_app.git>
cd <news_application>
2. Create and Activate a Virtual Environment

python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
3. Install Dependencies

pip install -r requirements.txt
4. Configure Environment Variables

Create a .env file in the root directory and add the following variables:

DB_NAME=news_application
DB_USER=news_user
DB_PASSWORD=Strongpass123
DB_HOST=127.0.0.1
DB_PORT=3306
Note: Do not commit this file. It is excluded via .gitignore.

5. Apply Migrations

python manage.py migrate
6. Load Backup Data (Optional)

python manage.py loaddata backup.json
7. Run the Development Server

python manage.py runserver
Access the application at:

http://127.0.0.1:8000


Running the Application with Docker

1. Build and Start Containers

docker-compose up --build
2. Apply Migrations (if not executed automatically)

docker-compose exec web python manage.py migrate
3. Load Backup Data

docker-compose exec web python manage.py loaddata /app/backup.json
4. Access the Application

http://localhost:8000


Environment Variables

Sensitive information such as database credentials is not stored in the repository. To run the application, create a .env file with the required variables.

Example:

DB_NAME=news_application
DB_USER=news_user
DB_PASSWORD=your_password
DB_HOST=db
DB_PORT=3306
.gitignore

The following files and directories are excluded from version control:

.env
venv/
__pycache__/
db.sqlite3
*.pyc
This ensures that sensitive information and unnecessary files are not committed to the repository.

Documentation

Sphinx documentation is available in:

docs/build/html/index.html

Notes for Reviewer

A sample backup file (backup.json) is included to populate the database.

Any required credentials are provided separately for review purposes and should not be committed to the repository.

Summary

Use a virtual environment for local development.

Use Docker for a containerized setup.

Store sensitive configuration in a .env file.

Do not commit secrets to version control.

Author

Siphokuhle Majozi