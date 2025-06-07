#!/usr/bin/env python3
"""
CareLedger Enhanced UI Setup Script
Automates the setup of enhanced UI components for CareLedger
"""

import os
import shutil
import json
from pathlib import Path
import subprocess
import sys

class CareLedgerUISetup:
    def __init__(self):
        self.project_root = Path.cwd()
        self.app_dir = self.project_root / "app"
        self.static_dir = self.app_dir / "static"
        self.templates_dir = self.app_dir / "templates"
        
        self.css_dir = self.static_dir / "css"
        self.js_dir = self.static_dir / "js"
        self.images_dir = self.static_dir / "images"
        
    def print_header(self):
        print("=" * 60)
        print("🚀 CareLedger Enhanced UI Setup")
        print("=" * 60)
        print("This script will set up the enhanced UI components for your")
        print("CareLedger orphanage inventory management system.")
        print()

    def check_environment(self):
        print("🔍 Checking environment...")
        
        # Check if we're in a CareLedger project
        if not self.app_dir.exists():
            print("❌ Error: app/ directory not found.")
            print("   Please run this script from your CareLedger project root.")
            return False
            
        # Check if Flask app structure exists
        required_files = [
            self.app_dir / "__init__.py",
            self.app_dir / "models.py",
            self.app_dir / "routes.py"
        ]
        
        for file_path in required_files:
            if not file_path.exists():
                print(f"⚠️  Warning: {file_path} not found.")
        
        print("✅ Environment check completed.")
        return True

    def backup_existing_files(self):
        print("💾 Creating backup of existing files...")
        
        backup_dir = self.project_root / "backup_ui_files"
        backup_dir.mkdir(exist_ok=True)
        
        # Backup templates
        if self.templates_dir.exists():
            shutil.copytree(
                self.templates_dir, 
                backup_dir / "templates", 
                dirs_exist_ok=True
            )
            print("   📁 Templates backed up")
        
        # Backup static files
        if self.static_dir.exists():
            shutil.copytree(
                self.static_dir, 
                backup_dir / "static", 
                dirs_exist_ok=True
            )
            print("   📁 Static files backed up")
        
        print(f"✅ Backup created in: {backup_dir}")

    def create_directories(self):
        print("📁 Creating directory structure...")
        
        directories = [
            self.css_dir,
            self.js_dir,
            self.images_dir,
            self.templates_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ {directory}")

    def create_enhanced_css(self):
        print("🎨 Creating enhanced CSS file...")
        
        css_content = '''/* CareLedger Enhanced Styles - Auto-generated */
/* This is a placeholder - replace with the actual enhanced-styles.css content */

:root {
    --primary-color: #2563eb;
    --primary-hover: #1d4ed8;
    --success-color: #16a34a;
    --warning-color: #d97706;
    --danger-color: #dc2626;
    --info-color: #0891b2;
    --dark-color: #1f2937;
    --light-bg: #f8fafc;
    --border-color: #e2e8f0;
    --text-muted: #64748b;
    --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    --border-radius: 12px;
    --border-radius-sm: 8px;
    --transition-normal: 0.3s ease;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background-color: var(--light-bg);
    line-height: 1.6;
    color: var(--dark-color);
}

.navbar {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
    box-shadow: var(--shadow-lg);
    border: none;
    padding: 1rem 0;
}

.card {
    border: none;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-md);
    transition: var(--transition-normal);
    background: white;
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
}

.btn {
    border-radius: var(--border-radius-sm);
    font-weight: 500;
    padding: 0.75rem 1.5rem;
    transition: var(--transition-normal);
    border: none;
}

.btn-primary {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
    box-shadow: var(--shadow-sm);
}

.btn-primary:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
}

/* Add more styles as needed */'''
        
        css_file = self.css_dir / "enhanced-styles.css"
        css_file.write_text(css_content)
        print(f"   ✅ Created: {css_file}")

    def create_enhanced_js(self):
        print("⚡ Creating enhanced JavaScript file...")
        
        js_content = '''// CareLedger Enhanced JavaScript - Auto-generated
// This is a placeholder - replace with the actual enhanced-app.js content

class EnhancedApp {
    constructor() {
        this.isTouch = 'ontouchstart' in window;
        this.isMobile = window.innerWidth < 768;
        this.notifications = [];
        
        this.bindEvents();
        this.initializeComponents();
    }

    static init() {
        if (!window.careLedgerApp) {
            window.careLedgerApp = new EnhancedApp();
        }
        return window.careLedgerApp;
    }

    bindEvents() {
        window.addEventListener('resize', this.handleResize.bind(this));
        window.addEventListener('scroll', this.handleScroll.bind(this));
        document.addEventListener('click', this.handleClick.bind(this));
    }

    initializeComponents() {
        this.initializeAnimations();
        this.initializeSearch();
        this.initializeMobileEnhancements();
        this.initializeTooltips();
    }

    initializeAnimations() {
        // Animation logic here
    }

    initializeSearch() {
        // Search enhancement logic here
    }

    initializeMobileEnhancements() {
        if (this.isMobile) {
            // Mobile-specific enhancements
        }
    }

    initializeTooltips() {
        // Tooltip initialization
    }

    handleResize() {
        this.isMobile = window.innerWidth < 768;
    }

    handleScroll() {
        // Scroll handling
    }

    handleClick(e) {
        // Click handling with animations
    }

    showNotification(message, type = 'info') {
        console.log(`${type.toUpperCase()}: ${message}`);
        // Notification display logic
    }
}

// Auto-initialize
document.addEventListener('DOMContentLoaded', () => EnhancedApp.init());

// Global utilities
window.showNotification = (message, type) => {
    if (window.careLedgerApp) {
        return window.careLedgerApp.showNotification(message, type);
    }
};

window.EnhancedApp = EnhancedApp;'''
        
        js_file = self.js_dir / "enhanced-app.js"
        js_file.write_text(js_content)
        print(f"   ✅ Created: {js_file}")

    def create_default_avatar(self):
        print("👤 Creating default avatar...")
        
        # Create a simple SVG avatar as placeholder
        svg_content = '''<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
    <circle cx="50" cy="50" r="50" fill="#e2e8f0"/>
    <circle cx="50" cy="35" r="15" fill="#94a3b8"/>
    <path d="M20 80 Q20 65 35 65 L65 65 Q80 65 80 80 Z" fill="#94a3b8"/>
</svg>'''
        
        avatar_file = self.images_dir / "default-avatar.svg"
        avatar_file.write_text(svg_content)
        print(f"   ✅ Created: {avatar_file}")

    def create_sample_templates(self):
        print("📄 Creating sample template files...")
        
        # Base template placeholder
        base_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}CareLedger{% endblock %}</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <!-- Enhanced Styles -->
    <link href="{{ url_for('static', filename='css/enhanced-styles.css') }}" rel="stylesheet">
    
    {% block styles %}{% endblock %}
</head>
<body>
    <!-- Enhanced Navigation -->
    <nav class="navbar navbar-expand-lg fixed-top">
        <div class="container-fluid">
            <a class="navbar-brand text-white" href="#">
                <i class="fas fa-heart me-2"></i>CareLedger
            </a>
            <!-- Add your navigation items here -->
        </div>
    </nav>

    <!-- Main Content -->
    <main style="margin-top: 90px; padding: 2rem 0;">
        {% block content %}{% endblock %}
    </main>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{{ url_for('static', filename='js/enhanced-app.js') }}"></script>
    {% block scripts %}{% endblock %}
</body>
</html>'''
        
        base_file = self.templates_dir / "base_enhanced.html"
        base_file.write_text(base_template)
        print(f"   ✅ Created: {base_file}")

    def update_requirements(self):
        print("📦 Checking Python requirements...")
        
        requirements_file = self.project_root / "requirements.txt"
        
        # Add any new requirements if needed
        new_requirements = [
            "Pillow>=9.0.0  # For image handling"
        ]
        
        if requirements_file.exists():
            current_reqs = requirements_file.read_text()
            for req in new_requirements:
                if req.split('>=')[0] not in current_reqs:
                    print(f"   📝 Consider adding: {req}")
        else:
            print("   ⚠️  requirements.txt not found")

    def create_setup_summary(self):
        print("📋 Creating setup summary...")
        
        summary = {
            "enhanced_ui_setup": {
                "version": "1.0.0",
                "date": "2024-12-19",
                "files_created": [
                    "app/static/css/enhanced-styles.css",
                    "app/static/js/enhanced-app.js",
                    "app/static/images/default-avatar.svg",
                    "app/templates/base_enhanced.html"
                ],
                "next_steps": [
                    "Replace CSS/JS placeholders with actual enhanced code",
                    "Update your existing templates to extend base_enhanced.html",
                    "Add optional API endpoints for enhanced functionality",
                    "Test on mobile, tablet, and desktop devices",
                    "Customize colors and branding in CSS variables"
                ],
                "documentation": "See the Implementation Guide for detailed instructions"
            }
        }
        
        summary_file = self.project_root / "enhanced_ui_setup.json"
        summary_file.write_text(json.dumps(summary, indent=2))
        print(f"   ✅ Created: {summary_file}")

    def print_next_steps(self):
        print("\n" + "=" * 60)
        print("✅ Enhanced UI Setup Complete!")
        print("=" * 60)
        print()
        print("📋 Next Steps:")
        print("1. Replace the placeholder CSS and JS files with the actual enhanced code")
        print("2. Update your existing templates to use the new base template")
        print("3. Test the enhanced UI on different devices")
        print("4. Customize colors and branding to match your organization")
        print("5. Add optional API endpoints for advanced features")
        print()
        print("📚 Documentation:")
        print("- Check enhanced_ui_setup.json for a summary")
        print("- Review the Implementation Guide for detailed instructions")
        print("- Test on mobile, tablet, and desktop devices")
        print()
        print("🎉 Your CareLedger UI is ready for enhancement!")
        print("=" * 60)

    def run_setup(self):
        try:
            self.print_header()
            
            if not self.check_environment():
                return False
            
            # Get user confirmation
            response = input("Continue with setup? (y/N): ").lower().strip()
            if response != 'y':
                print("Setup cancelled.")
                return False
            
            self.backup_existing_files()
            self.create_directories()
            self.create_enhanced_css()
            self.create_enhanced_js()
            self.create_default_avatar()
            self.create_sample_templates()
            self.update_requirements()
            self.create_setup_summary()
            self.print_next_steps()
            
            return True
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False

def main():
    setup = CareLedgerUISetup()
    success = setup.run_setup()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()