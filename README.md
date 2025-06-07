# CareLedger - Orphanage Inventory Management System

A comprehensive Flask-based web application designed to help orphanages manage their inventory, track usage, and forecast future needs using AI-powered analytics.

## Features

### 🔐 User Management & Authentication
- Role-based access control (Admin, Manager, Staff)
- User registration and profile management
- Secure login with CSRF protection
- Multi-orphanage support with user assignments

### 📊 Dashboard & Analytics
- Real-time inventory overview
- Usage analytics and trends
- Low stock alerts and notifications
- Mobile-responsive design

### 🎯 AI-Powered Forecasting
- Predictive analytics for inventory needs
- Usage pattern analysis
- Automated reorder suggestions
- Historical data insights

### 📱 Mobile-First Design
- Responsive layout optimized for mobile devices
- Touch-friendly interface
- Hamburger navigation menu
- Optimized card layouts for small screens

### 📈 Reports & Management
- Comprehensive inventory reports
- Usage tracking and logs
- Item management with categories
- Historical usage analysis

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Authentication**: Flask-Login with password hashing
- **Forms**: Flask-WTF with CSRF protection
- **Database Migrations**: Flask-Migrate
- **AI Integration**: Ready for Gemini API integration

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd careLedger
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database**
   ```bash
   flask db upgrade
   python add_auth_tables.py  # Add initial data
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

The application will be available at `http://localhost:5000`

## Configuration

### Environment Variables (.env)
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///instance/careledger.db
GEMINI_API_KEY=your-gemini-api-key
FLASK_ENV=development
```

### Default Admin Account
- **Username**: admin
- **Password**: admin123
- **Role**: Administrator

*Change these credentials immediately after first login*

## Project Structure

```
careLedger/
├── app/
│   ├── __init__.py          # Flask app initialization
│   ├── models.py            # Database models
│   ├── routes.py            # Main application routes
│   ├── services.py          # Business logic services
│   ├── ai_forecasting.py    # AI integration module
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── routes.py        # Authentication routes
│   │   └── forms.py         # Authentication forms
│   ├── templates/           # Jinja2 templates
│   │   ├── base.html        # Base template with mobile optimization
│   │   ├── dashboard.html   # Main dashboard
│   │   ├── auth/           # Authentication templates
│   │   └── errors/         # Error page templates
│   └── static/
│       └── css/            # Custom CSS files
├── migrations/             # Database migration files
├── instance/              # Instance-specific files (databases, configs)
├── config.py             # Application configuration
├── requirements.txt      # Python dependencies
└── run.py               # Application entry point
```

## Key Features in Detail

### Mobile Optimization
- **Responsive Navigation**: Collapsible hamburger menu for mobile
- **Card Layouts**: 2-per-row on mobile, 4-per-row on desktop
- **Touch-Friendly**: Optimized button sizes and spacing
- **Mobile Header**: Compact header design with user dropdown

### Security Features
- CSRF protection on all forms
- Password hashing with Werkzeug
- Session management with secure cookies
- Role-based route protection

### Database Models
- **User**: Authentication and profile information
- **Role**: User permission levels
- **Orphanage**: Multi-organization support
- **InventoryItem**: Product information and stock levels
- **UsageLog**: Historical usage tracking

## API Integration

The application is prepared for AI integration with:
- Gemini API for forecasting
- RESTful endpoints for data access
- JSON response formatting
- Error handling and logging

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in this repository
- Contact the development team
- Check the documentation in the `docs/` folder

## Version History

- **v1.0.0** - Initial release with core inventory management
- **v1.1.0** - Added mobile optimization and responsive design
- **v1.2.0** - Enhanced user management and role-based access
- **v1.3.0** - AI forecasting integration and advanced analytics

---

Built with ❤️ for orphanages and care organizations worldwide.
