# DjangoGramm

A social media platform built with Django, inspired by Instagram. DjangoGramm allows users to share photos, follow other users, like and comment on posts, and interact with a community of photographers and content creators.

## 🚀 Features

- **User Authentication**: 
  - Traditional email/password registration and login
  - Social authentication (Google OAuth2, GitHub)
  - Secure password reset functionality
- **User Profiles**: Customizable user profiles with bio, profile pictures, and personal information
- **Photo Sharing**: 
  - Upload and share photos with captions
  - Cloud-based image storage using Cloudinary
  - Automatic image optimization
- **Social Interactions**: 
  - Follow/unfollow other users
  - Like and unlike posts
  - Comment on posts
  - Reply to comments
- **Feed System**: Personalized feed showing posts from followed users
- **Explore Page**: Discover new content and users
- **Search Functionality**: Search for users and hashtags
- **Responsive Design**: Mobile-friendly interface using modern CSS
- **Real-time Notifications**: Get notified about likes, comments, and new followers
- **Direct Messaging**: Send private messages to other users

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package manager)
- Git
- PostgreSQL (recommended) or SQLite for development
- Virtual environment tool (venv or virtualenv)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/FunkyDrama/DjangoGramm.git
cd DjangoGramm
```

### 2. Create Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Create a `.env` file in the project root directory:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://username:password@localhost/djangogramm
ALLOWED_HOSTS=localhost,127.0.0.1

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password

# Cloudinary Configuration (for image storage)
CLOUD_NAME=your-cloudinary-cloud-name
API_KEY=your-cloudinary-api-key
API_SECRET=your-cloudinary-api-secret
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name

# Social Authentication - Google
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=your-google-oauth2-key
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=your-google-oauth2-secret

# Social Authentication - GitHub
SOCIAL_AUTH_GITHUB_KEY=your-github-oauth-key
SOCIAL_AUTH_GITHUB_SECRET=your-github-oauth-secret
```

### 5. Database Setup

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (admin)
python manage.py createsuperuser
```

### 6. Static Files

```bash
python manage.py collectstatic
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser to see the application.

## 📂 Project Structure

```
DjangoGramm/
│
├── djangogramm/           # Main project directory
│   ├── __init__.py
│   ├── settings.py        # Django settings
│   ├── urls.py           # Main URL configuration
│   ├── wsgi.py           # WSGI configuration
│   └── asgi.py           # ASGI configuration
│
├── apps/                  # Django applications
│   ├── accounts/         # User authentication and profiles
│   ├── posts/            # Post management
│   ├── comments/         # Comment system
│   ├── likes/            # Like functionality
│   ├── follows/          # Follow system
│   └── notifications/    # Notification system
│
├── static/               # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── img/
│
├── media/                # User-uploaded files
│   ├── profiles/
│   └── posts/
│
├── templates/            # HTML templates
│   ├── base.html
│   ├── registration/
│   └── includes/
│
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables example
├── .gitignore          # Git ignore file
└── README.md           # Project documentation
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test apps.posts

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 🚀 Deployment

### Heroku Deployment

1. Install Heroku CLI and login:
```bash
heroku login
```

2. Create a new Heroku app:
```bash
heroku create djangogramm-app
```

3. Set environment variables:
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
```

4. Add PostgreSQL:
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

5. Deploy:
```bash
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### Docker Deployment

Build and run with Docker:

```bash
# Build the image
docker build -t djangogramm .

# Run the container
docker run -p 8000:8000 djangogramm
```

## 🔧 Configuration

### Database Configuration

The project supports multiple databases. Configure in `settings.py`:

```python
# PostgreSQL (Recommended for production)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'djangogramm',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Cloudinary Configuration

The project uses Cloudinary for image storage and optimization:

```python
import cloudinary
import cloudinary.uploader
import cloudinary.api

cloudinary.config(
    cloud_name = os.environ.get('CLOUD_NAME'),
    api_key = os.environ.get('API_KEY'),
    api_secret = os.environ.get('API_SECRET')
)
```

To set up Cloudinary:
1. Create a free account at [Cloudinary](https://cloudinary.com)
2. Get your credentials from the dashboard
3. Add them to your `.env` file

### Social Authentication Setup

#### Google OAuth2
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs: `http://localhost:8000/complete/google-oauth2/`
6. Copy the Client ID and Client Secret to your `.env` file

#### GitHub OAuth
1. Go to GitHub Settings > Developer settings > OAuth Apps
2. Click "New OAuth App"
3. Set Authorization callback URL: `http://localhost:8000/complete/github/`
4. Copy the Client ID and Client Secret to your `.env` file

### Email Configuration

Set up email for notifications and password reset:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
```

For Gmail, you may need to:
1. Enable 2-factor authentication
2. Generate an app-specific password
3. Use the app password in your `.env` file

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Write tests for new features

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django Documentation
- TailwindCSS for responsive design
- Font Awesome for icons
- Pillow for image processing
- Django REST Framework for API development

## 📞 Contact

Project Creator: [FunkyDrama](https://github.com/FunkyDrama)

Project Link: [https://github.com/FunkyDrama/DjangoGramm](https://github.com/FunkyDrama/DjangoGramm)

## 🐛 Bug Reports

If you discover any bugs, please create an issue [here](https://github.com/FunkyDrama/DjangoGramm/issues) including:
1. Description of the bug
2. Steps to reproduce
3. Expected behavior
4. Screenshots (if applicable)
5. System information

## ⭐ Support

If you find this project helpful, please give it a ⭐ on GitHub!

---

**Happy Coding!** 🚀
