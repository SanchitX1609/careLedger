#!/usr/bin/env python3
"""
careLedger - Supply Chain & Inventory Management System for Orphanages
Main application entry point
"""

import os
from app import create_app

# Create Flask application
app = create_app(os.getenv('FLASK_CONFIG', 'default'))

if __name__ == '__main__':
    # Run the application
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.getenv('PORT', 5001))
    
    print("🏠 Starting careLedger - Inventory Management System for Orphanages")
    print(f"🌐 Running on http://localhost:{port}")
    print("📊 Dashboard will be available at the root URL")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
