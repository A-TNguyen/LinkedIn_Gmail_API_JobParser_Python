# Setting Up Credentials

This guide will help you set up the necessary credentials for the LinkedIn Job Application Tracker.

## Prerequisites

1. A Google Account
2. Access to Google Cloud Console
3. Python 3.7 or higher installed

## Step 1: Set Up Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Enable the Gmail API for your project
4. Configure the OAuth consent screen:
   - Go to "APIs & Services" > "OAuth consent screen"
   - Choose "External" user type
   - Fill in the required information
   - Add the following scopes:
     - `https://www.googleapis.com/auth/gmail.readonly`
     - `https://www.googleapis.com/auth/gmail.modify`

## Step 2: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Desktop application" as the application type
4. Name your OAuth client
5. Click "Create"
6. Download the credentials file (it will be named something like `client_secret_*.json`)

## Step 3: Set Up Environment Variables

1. Copy the `env.example` file to `.env`:
   ```bash
   cp env.example .env
   ```

2. Open the downloaded credentials file and copy the values:
   - `client_id` → `GMAIL_CLIENT_ID`
   - `client_secret` → `GMAIL_CLIENT_SECRET`
   - The redirect URI should be `http://localhost:8080/`

3. Edit the `.env` file and replace the placeholder values with your actual credentials:
   ```
   GMAIL_CLIENT_ID=your_actual_client_id
   GMAIL_CLIENT_SECRET=your_actual_client_secret
   GMAIL_REDIRECT_URI=http://localhost:8080/
   ```

## Step 4: First-Time Authentication

When you run the application for the first time:

1. The application will open your default web browser
2. Sign in with your Google account
3. Grant the requested permissions
4. The application will automatically save the token for future use

## Security Best Practices

### Protected Files

The `.gitignore` file is configured to automatically exclude these sensitive files:

**Authentication & Configuration:**
- `.env` - Environment variables
- `credentials.json` - Google API credentials  
- `token.json` - OAuth access tokens
- `client_secret*.json` - Downloaded OAuth files
- `config/` - Entire configuration directory

**Generated Data & Logs:**
- `*.log` - All log files
- `*.csv` - CSV output files (may contain personal data)
- `*.xlsx` - Excel output files
- `src/logs/` - Application logs directory
- `src/data/` - All data directories

### Security Guidelines

1. **Credential Management:**
   - Store credentials only in the `config/` directory
   - Never commit or share credential files
   - Use environment variables when possible
   - Rotate credentials regularly

2. **File Permissions:**
   - Set restrictive permissions on sensitive files (600 on Unix)
   - Keep credential files in secure locations
   - Regularly audit file access

3. **Development Practices:**
   - Use separate credentials for development/production
   - Never hardcode credentials in source code
   - Review `.gitignore` before committing changes
   - Use secure backup methods for credential files

## Troubleshooting

If you encounter authentication issues:

1. Check that your credentials are correctly set in the `.env` file
2. Ensure the Gmail API is enabled in your Google Cloud Console
3. Verify that the OAuth consent screen is properly configured
4. Delete the `token.json` file and try authenticating again
5. Check that your system time is correctly set (OAuth is time-sensitive)

## Support

If you need help with credential setup:
1. Check the [Google Cloud Console documentation](https://cloud.google.com/docs)
2. Review the [Gmail API documentation](https://developers.google.com/gmail/api/guides)
3. Open an issue in this repository for specific problems 