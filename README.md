# 🏋️ Gym API

A full-stack gym management application built with **Flask** (Python) for the backend API and frontend templates, served on a single port. Manage gym members, track daily entries, handle admin authentication, and record user biometrics.

---

## 📋 Requirements

### System Requirements

| Software   | Version     |
|------------|-------------|
| Python     | 3.11+       |
| pip        | latest      |
| MySQL      | 5.7+ / 8.0+ |

### Python Dependencies (`requirements.txt`)

| Package                | Purpose                                      |
|------------------------|----------------------------------------------|
| Flask                  | Web framework (backend + frontend templates) |
| Flask-Cors             | Cross-Origin Resource Sharing support        |
| mysql-connector-python | MySQL database driver                        |
| bcrypt                 | Password hashing for admin authentication    |
| PyJWT                  | JSON Web Token generation & verification     |
| python-dotenv          | Load environment variables from `.env`       |
| gunicorn               | Production WSGI server                       |
| requests               | HTTP client library                          |
| Pillow                 | Image processing (thumbnails for user photos)|

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
GYM_DB_PORT=3306
GYM_DB_SERVER=localhost
GYM_DB_USERNAME=your_db_user
GYM_DB_PASSWORD=your_db_password
GYM_DB_NAME=gyms
SECRET_KEY=your_secret_key
PORT=3001
```

---

## 🚀 Installation

### Option 1 — Local Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd gym_api
   ```

2. **Create and activate a virtual environment**

   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the database**

   - Create a MySQL database named `gyms`.
   - Run the SQL schema (see [Database Schema](#-database-schema) below) to create the required tables.
   - Update the `.env` file with your database credentials.

5. **Run the application**

   ```bash
   python app.py
   ```

   The app will start on **http://localhost:3001**.

### Option 2 — Docker

1. **Build the Docker image**

   ```bash
   docker build -t gym-api .
   ```

2. **Run the container**

   ```bash
   docker run -d -p 3000:3000 --env-file .env gym-api
   ```

### Option 3 — Docker Compose (with ngrok tunnel)

```bash
docker-compose up --build
```

This starts the Flask app and an ngrok tunnel (web interface at `http://localhost:4040`).

---

## 🧪 Testing

The application uses `pytest` for unit testing. The test files are located in the `tests/` directory.

To run the tests, ensure your virtual environment is activated and use the following command from the project root:

```bash
pytest tests/
```

---

## 📖 How to Use

### 1. Access the Application

Open your browser and navigate to:

```
http://localhost:3001
```

### 2. Login

- You will see the **login page** (`/`).
- Enter the admin email and password to authenticate.
- On successful login, a JWT token is stored in the browser's `localStorage`.

### 3. Frontend Pages

Once logged in, use the bottom navigation bar to access:

| Page               | Route           | Description                                     |
|--------------------|-----------------|--------------------------------------------------|
| **Login**          | `/`             | Admin login page                                 |
| **Dashboard**      | `/dashboard`    | Overview dashboard                               |
| **Today's Entries**| `/entries`      | View all gym entries for the current day          |
| **Add Entry**      | `/add-entry`    | Register a new gym entry for a user              |
| **Manage Users**   | `/manage-users` | List, search, and manage gym members             |
| **Add User**       | `/add-user`     | Register a new gym member                        |
| **User Details**   | `/user`         | View and edit a specific user's profile          |
| **User Biometrics**| `/biometrics`   | View and record biometric data (weight, height…) |
| **Edit Gym**       | `/edit-gym`     | Update gym name, logo, and background image      |
| **Forgot Password**| `/forgot`       | Request a verification code to reset password    |
| **Reset Password** | `/reset`        | Reset admin password with verification code      |

### 4. REST API Endpoints

All API routes are prefixed with `/api`. Most endpoints require a JWT `Authorization: Bearer <token>` header.

#### Authentication

| Method | Endpoint                | Auth | Description                          |
|--------|-------------------------|------|--------------------------------------|
| POST   | `/api/login`            | ✗    | Admin login, returns JWT token       |
| POST   | `/api/send-password-code`| ✗   | Send verification code to admin email|
| POST   | `/api/reset-password`   | ✗    | Reset password using code            |

#### Users

| Method | Endpoint                    | Auth | Description                           |
|--------|-----------------------------|------|---------------------------------------|
| POST   | `/api/users`                | ✗    | Create a new gym member               |
| GET    | `/api/users/<user_id>`      | ✓    | Get user details by ID                |
| PUT    | `/api/users/<user_id>`      | ✓    | Update user (name, exp, image)        |
| PUT    | `/api/users`                | ✓    | Update user (name, exp) by body ID    |
| GET    | `/api/users/gym/<gym_id>`   | ✓    | Get all users belonging to a gym      |

#### Entries

| Method | Endpoint                      | Auth | Description                        |
|--------|-------------------------------|------|------------------------------------|
| POST   | `/api/entries`                | ✓    | Register a new gym entry           |
| GET    | `/api/entries/today/<gym_id>` | ✓    | Get today's entries for a gym      |
| GET    | `/api/entries/user/<user_id>` | ✓    | Get all entries for a specific user|

#### Gyms

| Method | Endpoint              | Auth | Description                        |
|--------|-----------------------|------|------------------------------------|
| GET    | `/api/gyms`           | ✓    | List all gyms                      |
| GET    | `/api/gym/<gym_id>`   | ✓    | Get a specific gym's details       |
| PUT    | `/api/gym/<gym_id>`   | ✓    | Update gym (name, logo, background)|

#### Biometrics

| Method | Endpoint                      | Auth | Description                        |
|--------|-------------------------------|------|------------------------------------|
| GET    | `/api/biometrics/<user_id>`   | ✓    | Get biometric records for a user   |
| POST   | `/api/biometrics`             | ✓    | Add a new biometric record         |

---

## 🗄️ Database Schema

The application uses a MySQL database named **`gyms`** with the following tables:

### `admin`

Stores gym administrator accounts used for login and authentication.

| Column            | Type          | Description                                |
|-------------------|---------------|--------------------------------------------|
| `id`              | INT (PK)      | Auto-increment primary key                 |
| `email`           | VARCHAR       | Admin email (unique, used for login)       |
| `password`        | VARCHAR       | Bcrypt-hashed password                     |
| `verify_code`     | VARCHAR (NULL)| Temporary verification code for password reset |
| `verify_code_exp` | DATETIME (NULL)| Expiration time for the verification code |

### `gym`

Stores gym information. Each gym is linked to an admin.

| Column     | Type          | Description                                    |
|------------|---------------|------------------------------------------------|
| `id`       | INT (PK)      | Auto-increment primary key                     |
| `name`     | VARCHAR       | Gym name                                       |
| `admin_id` | INT (FK)      | References `admin.id` — the gym's owner        |
| `image`    | LONGBLOB (NULL)| Gym logo image stored as binary                |
| `back`     | LONGBLOB (NULL)| Gym background image stored as binary          |

### `users`

Stores gym members. Each user belongs to one gym.

| Column   | Type          | Description                                      |
|----------|---------------|--------------------------------------------------|
| `id`     | INT (PK)      | Auto-increment primary key                       |
| `name`   | VARCHAR       | Member's full name                               |
| `exp`    | DATE          | Membership expiration date                       |
| `gym_id` | INT (FK)      | References `gym.id` — the gym this user belongs to |
| `image`  | LONGBLOB (NULL)| User profile photo stored as binary              |

### `entries`

Tracks gym check-in entries. Each entry links a user to a gym on a specific date.

| Column     | Type          | Description                                  |
|------------|---------------|----------------------------------------------|
| `id`       | INT (PK)      | Auto-increment primary key                   |
| `users_id` | INT (FK)      | References `users.id` — the member checking in |
| `gym_id`   | INT (FK)      | References `gym.id` — the gym location       |
| `day`      | DATETIME      | Timestamp of the entry (defaults to `NOW()`) |

### `biometrcs`

Stores biometric measurements for gym members over time.

| Column    | Type          | Description                              |
|-----------|---------------|------------------------------------------|
| `id`      | INT (PK)      | Auto-increment primary key               |
| `user_id` | INT (FK)      | References `users.id`                    |
| `peso`    | DECIMAL/FLOAT | Weight (in kg)                           |
| `altura`  | DECIMAL/FLOAT | Height (in cm)                           |
| `cintura` | DECIMAL/FLOAT | Waist measurement (in cm)                |
| `bmg`     | DECIMAL/FLOAT | Body mass/fat percentage                 |
| `date`    | DATETIME      | Date of the measurement                  |

### Entity Relationship Diagram

```
┌──────────┐       ┌──────────┐       ┌──────────┐
│  admin   │       │   gym    │       │  users   │
├──────────┤       ├──────────┤       ├──────────┤
│ id (PK)  │──1:1──│ admin_id │       │ id (PK)  │
│ email    │       │ id (PK)  │──1:N──│ gym_id   │
│ password │       │ name     │       │ name     │
│ verify_  │       │ image    │       │ exp      │
│   code   │       │ back     │       │ image    │
└──────────┘       └──────────┘       └──────────┘
                                           │
                                          1:N
                                           │
                   ┌──────────┐       ┌──────────┐
                   │biometrcs │       │ entries  │
                   ├──────────┤       ├──────────┤
                   │ id (PK)  │       │ id (PK)  │
                   │ user_id  │───────│ users_id │
                   │ peso     │       │ gym_id   │
                   │ altura   │       │ day      │
                   │ cintura  │       └──────────┘
                   │ bmg      │
                   │ date     │
                   └──────────┘
```

---

## 📁 Project Structure

```
gym_api/
├── app.py                  # Flask application entry point (port 3001)
├── db.py                   # MySQL database connection helper
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not committed)
├── Dockerfile              # Docker image configuration
├── docker-compose.yml      # Docker Compose (app + ngrok)
├── routes/
│   └── api.py              # Flask Blueprint — all /api/* endpoints
├── utils/
│   └── auth.py             # JWT token generation & authentication decorator
├── templates/
│   ├── base.html           # Base Jinja2 template with navigation
│   ├── index.html          # Login page
│   ├── dashboard.html      # Dashboard
│   ├── entries_today.html  # Today's entries
│   ├── add_entry.html      # Add entry form
│   ├── manage_users.html   # User management list
│   ├── add_user.html       # Add user form
│   ├── user.html           # User detail / edit page
│   ├── user_biometrics.html# Biometrics tracking page
│   ├── edit_gym.html       # Gym settings page
│   ├── forgot.html         # Forgot password page
│   └── reset.html          # Reset password page
├── static/
│   ├── scripts.js          # Shared frontend JavaScript
│   └── default-bg.jpg      # Default background image
└── nginx.conf/             # Nginx configuration
```

---

## 📝 Notes

- The **Flask app** (`app.py`) is the server. It serves both the HTML frontend (via Jinja2 templates) and the REST API (via the `/api` Blueprint) on **port 3001**.
- User and gym images are stored as **binary BLOBs** in MySQL and transferred as **base64-encoded** strings via the API.
- Admin passwords are hashed with **bcrypt** before storage.
- JWT tokens expire after **1 day** and must be included as `Authorization: Bearer <token>` in API requests.
