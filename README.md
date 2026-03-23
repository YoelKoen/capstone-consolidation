# NewsEngine Capstone

**A Robust News Ecosystem with Role-Based Access Control & Automated Workflows**

## Project Overview

NewsEngine is a high-performance news platform designed to manage the lifecycle of digital journalism. The system bridges the gap between journalists and readers through a strict **Editor Approval Workflow**, ensuring content quality before publication.

The backend leverages **Django Signals** to automate side effects like social media distribution and email notifications upon article approval.

---

## Design Documentation

Before implementation, the following functional and non-functional requirements were identified:

### Functional Requirements

* **RBAC (Role-Based Access Control):**
    * **Readers:** View approved articles, comment, and subscribe to either an independent journalist or a publisher.
    * **Journalists:** Draft and submit articles and newsletters. 
        * *Constraint:* A journalist cannot publish independently; they must be assigned to a publishing house/employer.
        * *Permissions:* If logged in, a journalist can update and delete their own articles and newsletters.
    * **Editors:** Access the **Editor Desk** to manage the queue.
        * *Permissions:* Editors can update and delete any articles and newsletters across the platform.

* **Content Lifecycle:** State-machine logic ensuring articles start as `is_approved=False`.
* **RESTful API:** Full CRUD capabilities for third-party integration, documented via Swagger (OpenAPI 3.0).

### UI/UX Planning

* **Mobile-Responsive Design:** Built using Bootstrap 5 to ensure accessibility across devices.
* **User Feedback:** Integration of the Django Messages Framework to provide real-time success/error alerts during the approval and submission process.

---

## Prerequisites

* **Python:** 3.11 or higher
* **Database:** MariaDB (or MySQL)
* **Environment:** Virtualenv (recommended)

---

## Local Installation & Setup

### 1. Project Environment
Navigate into your project folder and set up a virtual environment to avoid dependency conflicts.

```bash
# Create the environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Mac/Linux
source venv/bin/activate

. Install Dependencies
Install the required packages using the refined requirements.txt.

Bash

pip install -r requirements.txt
3. Database Initialization
Ensure MariaDB is running. Access your SQL console and create the database:

SQL

CREATE DATABASE news_db;
4. Configure Credentials
Open news_system/settings.py and update the DATABASES dictionary with your local MariaDB password:

Python

'PASSWORD': 'YourActualPassword',
Running the Application
Once the database is configured, initialize the system with these commands:

Bash

# 1. Apply database migrations
python manage.py makemigrations news_engine
python manage.py migrate

# 2. Create the administrative 'Superuser' (Required for Editor access)
python manage.py createsuperuser

# 3. Start the development server
python manage.py runserver
Access the application at: http://127.0.0.1:8000/

Testing & API Documentation
Automated Testing
The project includes a comprehensive suite of unit tests covering authentication, permission guards, and approval signals.

Bash

python manage.py test news_engine
API Exploration (OpenAPI 3.0)
The RESTful API is fully documented and interactive:

Swagger UI: http://127.0.0.1:8000/api/docs/

Redoc: http://127.0.0.1:8000/api/redoc/

Project Structure & Separation of Concerns
/news_engine: Contains the core application logic (Models, Views, Serializers).

/news_engine/templates/news_engine/: Application-specific templates following Django best practices for namespacing.

/news_engine/signals.py: Handles post-save automation logic.

/news_system: Project-level configuration and routing.


---

### **Final Status of Your Checklist**
* [x] **Readme:** Removed `git clone` and `<repository_url>`.
* [x] **Journalist:** Assigned to publisher house; can submit newsletters; can edit/delete their own work.
* [x] **Editor:** Can edit/delete all content; Editor Desk template error resolved.
* [x] **Reader:** Can subscribe to journalists or publishers.

**Would you like me to generate the `news_engine/signals.py` file to handle the automated notifications mentioned in