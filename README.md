# Support System Project

A comprehensive support ticket management system built with Django, featuring both API and template-based interfaces.

## Features

- **User Management**: Registration, authentication, and role-based access control (Admin, Support, Client)
- **Ticket Management**: Create, update, assign, and track support tickets
- **Commenting System**: Add comments to tickets for communication
- **Notification System**: In-app and email notifications for ticket updates and comments
- **Dashboard**: Role-specific statistics and ticket overview
- **Responsive UI**: Modern interface built with Bootstrap

## Project Structure

- **accounts**: User management, authentication, and profile handling
- **tickets**: Ticket creation, management, and commenting functionality
- **notifications**: In-app and email notification system
- **templates**: HTML templates for the web interface
- **static**: CSS, JavaScript, and other static assets

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On Unix/MacOS
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Configure the database in `support_system/settings.py`
5. Run migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```
6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```
7. Run the development server:
   ```
   python manage.py runserver
   ```

## API Endpoints

### Authentication
- `POST /api/accounts/register/`: Register a new user
- `POST /api/accounts/token/`: Obtain JWT token
- `POST /api/accounts/token/refresh/`: Refresh JWT token

### Users
- `GET /api/accounts/users/`: List all users (admin only)
- `GET /api/accounts/users/<id>/`: Get user details
- `PUT /api/accounts/users/<id>/`: Update user profile

### Tickets
- `GET /api/tickets/tickets/`: List tickets (filtered by user role)
- `POST /api/tickets/tickets/`: Create a new ticket
- `GET /api/tickets/tickets/<id>/`: Get ticket details
- `PUT /api/tickets/tickets/<id>/`: Update a ticket
- `DELETE /api/tickets/tickets/<id>/`: Delete a ticket

### Comments
- `GET /api/tickets/comments/`: List comments
- `POST /api/tickets/comments/`: Add a comment to a ticket

### Departments & Categories
- `GET /api/tickets/departments/`: List departments
- `GET /api/tickets/categories/`: List categories

## Web Interface

- `/`: Home dashboard
- `/tickets/`: Ticket listing
- `/tickets/create/`: Create a new ticket
- `/tickets/<id>/`: View ticket details
- `/tickets/<id>/update/`: Update a ticket
- `/tickets/<id>/delete/`: Delete a ticket
- `/tickets/<id>/comment/`: Add a comment to a ticket
- `/accounts/login/`: User login
- `/accounts/logout/`: User logout
- `/accounts/register/`: User registration
- `/accounts/profile/`: View user profile
- `/accounts/profile/edit/`: Edit user profile
- `/notifications/list/`: View notifications
- `/notifications/preferences/`: Manage notification preferences

## License

This project is licensed under the MIT License - see the LICENSE file for details.