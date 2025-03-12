# Email Rule Manager

Transform your Gmail inbox management with our intelligent rule-based automation system. This application provides a seamless way to organize, categorize, and process your emails automatically.

## Key Features

- 🔒 Secure Gmail integration with OAuth 2.0 authentication
- ⚡ Real-time email synchronization and processing
- 💾 Robust SQLite-powered email storage system
- 🧠 Intelligent rule engine with flexible condition matching
- 🔄 Comprehensive email action system (moving, marking as read)
- 🎨 Modern, intuitive Streamlit dashboard

## Project Structure

```plaintext
├── src/                    # Source code directory
│   ├── __init__.py
│   ├── auth/              # Authentication related modules
│   │   ├── __init__.py
│   │   └── gmail_auth.py  # Gmail OAuth2 implementation
│   ├── database/          # Database operations
│   │   ├── __init__.py
│   │   └── data_store.py  # Email and rule storage
│   ├── email/             # Email handling
│   │   ├── __init__.py
│   │   └── email_handler.py # Email operations
│   ├── rules/             # Rule processing
│   │   ├── __init__.py
│   │   └── rule_engine.py # Rule execution logic
│   └── ui/                # User interface
│       ├── __init__.py
│       └── web_interface.py # Streamlit UI components
├── assets/                # Application assets
├── auth_manager.py        # Authentication manager
├── data_store.py         # Data storage operations
├── requirements.txt       # Project dependencies
├── rule_engine.py        # Rule processing logic
├── rules.json            # Rule definitions
├── web_interface.py      # Web interface components
└── .gitignore            # Git ignore file
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Active Gmail account
- Google Cloud Platform access

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd email-rule-manager
```

2. Set up your environment:
```bash
pip install -r requirements.txt
```

3. Google API Configuration:
   - Navigate to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable Gmail API
   - Configure OAuth 2.0 credentials
   - Download and save credentials as `credentials.json` in the project root

## Usage

1. Start the application:
```bash
python -m streamlit run src/ui/web_interface.py
```

2. Authenticate with Gmail:
   - Click the "🔐 Authenticate" button in the sidebar
   - Follow the OAuth2 flow to grant access
   - Once authenticated, you'll see a success message

3. Managing Emails:
   - Use the "📥 Fetch" button to sync recent emails
   - View email statistics and timeline
   - Monitor processing status

4. Creating Rules:
   - Navigate to the Rules tab
   - Click "Create Rule"
   - Set conditions and actions
   - Save and process emails

## Rule Configuration

Rules are defined in JSON format with conditions and actions:

```json
{
  "name": "Important Emails",
  "match_type": "any",
  "conditions": [
    {
      "field": "From",
      "operation": "contains",
      "value": "important@company.com"
    }
  ],
  "actions": [
    {
      "type": "Move Message",
      "value": "Important"
    }
  ]
}
```

## Screenshots

### Email Management Interface
![Email Management](assets\Email_management.png)
*Real-time email synchronization and processing dashboard*

### Rule Creation Interface
![Rule Creation](assets\Create_rules.png)
*Intuitive rule configuration with dynamic conditions*

### Processing rules interface
![Rule Creation](assets\process_rules.png)
*Processing of rules with fetched emails*

### Existing rules interface
![Rule Creation](assets\Existing rules.png)
*Rules that have been created already*

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.