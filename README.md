News Engine - Final Django Capstone
Introduction
The News Engine is a professional content management platform designed for digital journalism. This application allows administrators to manage news categories and articles, while providing a clean interface for readers to stay informed.

1. **Project Initialization**
`Create your virtual environment (Windows)`
`Initialize the virtual environment: python -m venv venv`

`Activate the virtual environment: .\venv\Scripts\activate`

`Install dependencies: pip install -r requirements.txt`

2. **Docker Orchestration (Recommended)**
`This project uses Docker Compose to manage the application and its database dependencies automatically.`

`Start the Services: docker-compose up --build`

`Database Healthcheck: The system is configured with a healthcheck that ensures the MariaDB container is fully initialized before the Django web service attempts to connect.`

`Apply Migrations (Internal): While the containers are running, run this in a new terminal:`

`docker-compose exec web python manage.py migrate`

3. **Tech Stack**
`This project utilizes a modern development stack:`

`Framework: Django 5.2.7`

`Database: MariaDB 10.6`

`Containerization: Docker & Docker Compose`

`Documentation: Sphinx`

4. **Database Configuration**
`The application is pre-configured to communicate with MariaDB.`

`Database Name: NewsApp_DB`

`User: root`

`Host: db (Internal Docker Network) or 127.0.0.1 (Local)`

`Port: 3307 (Mapped to 3306)`

5. **Final Launch Steps**
Final Launch Commands (Windows)
`Build the Database Structure: python manage.py migrate`

`Create the Administrator: python manage.py createsuperuser`

`Launch the Server: python manage.py runserver`

6. **Documentation & Repository**
`Sphinx Documentation: docs/build/html/index.html`

Remote Repository: `https://github.com/YoelKoen/capstone-consolidation`