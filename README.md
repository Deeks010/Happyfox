# Email Rule Manager

Transform your Gmail inbox management with our intelligent rule-based automation system. This application provides a seamless way to organize, categorize, and process your emails automatically.

## Key Features

- Secure Gmail integration with OAuth 2.0 authentication
- Real-time email synchronization and processing
- Robust SQLite-powered email storage system
- Intelligent rule engine with flexible condition matching
- Comprehensive email action system (labeling, status updates)
- Modern, intuitive Streamlit dashboard

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Active Gmail account
- Google Cloud Platform access

### Installation

1. Set up your environment:
```bash
pip install -r requirements.txt
```

2. Google API Configuration:
   - Navigate to [Google Cloud Console](https://console.cloud.google.com/)
   - Set up a new project
   - Configure Gmail API access
   - Generate OAuth 2.0 credentials
   - Save the credentials file as `credentials.json` in the project directory

## Application Structure

```plaintext
├── auth_manager.py     # OAuth authentication system
├── data_store.py      # Email database management
├── email_handler.py   # Email operations controller
├── rule_engine.py     # Rule processing system
├── models.py         # Data structures
├── web_interface.py  # Streamlit UI components
├── requirements.txt  # Dependencies
└── rules.json       # Rule definitions
```

## Interface Preview

### Email Fetching Dashboard
![Email Fetching Interface](path_to_fetch_emails_screenshot.png)
*Real-time email synchronization and storage visualization*

### Rule Creation Interface
![Rule Creation Dashboard](path_to_create_rules_screenshot.png)
*Intuitive rule configuration and management system*

## Quick Start Guide

1. Launch the application:
```bash
python -m streamlit run web_interface.py
```

2. Complete the Gmail authentication process
3. Access the rule management interface
4. Monitor email processing activities

## Rule Configuration Format

Customize email processing with JSON-based rules:

```json
{
  "rules": [
    {
      "name": "Priority Messages",
      "match_type": "any",
      "conditions": [
        {
          "field": "sender",
          "operation": "contains",
          "value": "priority@company.com"
        }
      ],
      "actions": [
        {
          "type": "apply_label",
          "label": "Priority"
        }
      ]
    }
  ]
}
```

## Development

Run the test suite:
```bash
python -m pytest tests/
```

## Contributing

We welcome contributions! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.