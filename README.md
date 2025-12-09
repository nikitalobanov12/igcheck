# igcheck

A CLI tool to find Instagram accounts you follow that don't follow you back.

## Installation

```bash
# Clone and install
cd igcheck
pip install -e .
```

## Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your Instagram credentials:
   ```
   IG_USERNAME=your_username
   IG_PASSWORD=your_password
   ```

## Usage

### Basic usage (uses credentials from .env or prompts)
```bash
igcheck
```

### With explicit credentials
```bash
igcheck --username myaccount --password mypassword
```

### Export to JSON
```bash
igcheck --json
igcheck --json --output my-results.json
```

### Export to CSV
```bash
igcheck --csv
igcheck --csv --output my-results.csv
```

### Interactive unfollow
```bash
igcheck --interactive
igcheck -i
```
This shows a checkbox list where you can select accounts to unfollow. Use arrow keys to navigate, Space to select/deselect, and Enter to confirm.

### All options
```
Usage: igcheck [OPTIONS]

  Find Instagram accounts you follow that don't follow you back.

Options:
  -u, --username TEXT  Instagram username (or set IG_USERNAME env var)
  -p, --password TEXT  Instagram password (or set IG_PASSWORD env var)
  --json               Output results as JSON
  --csv                Output results as CSV
  -o, --output PATH    Output file path
  -i, --interactive    Interactively select and unfollow accounts
  --help               Show this message and exit.
```

## Features

- Session persistence (avoids repeated logins)
- 2FA support (prompts for verification code when needed)
- Progress indicators while fetching data
- Multiple output formats (console, JSON, CSV)
- Rich console output with formatted tables
- Interactive unfollow with checkbox selection

## Security Notes

- Credentials are never stored in code
- Session data (`session.json`) is gitignored and contains auth tokens
- Use environment variables for credentials in scripts

## Troubleshooting

### "Instagram challenge required"
This happens when Instagram detects unusual login activity. Open the Instagram app on your phone, complete any security challenges, then try again.

### "Login failed"
Double-check your username and password. If you have 2FA enabled, make sure to enter the code when prompted.

### Rate limiting
Instagram may temporarily block requests if you make too many in a short time. Wait a few minutes and try again.
