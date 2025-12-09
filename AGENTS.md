# AGENTS.md

Project-specific guidance for working with the igcheck codebase.

## Project Overview

igcheck is a CLI tool that uses Instagram's private API (via `instagrapi`) to find accounts you follow that don't follow you back.

## Architecture

```
igcheck/
├── cli.py          # Click-based CLI entry point
├── instagram.py    # Instagram API wrapper (instagrapi)
└── output.py       # Output formatters (console/JSON/CSV)
```

### Key Components

- **InstagramClient** (`instagram.py:28`): Wrapper around instagrapi Client with session persistence and 2FA support
- **UserInfo** (`instagram.py:18`): Dataclass representing an Instagram user (user_id, username, full_name, profile_url)
- **Output functions** (`output.py`): `print_to_console()`, `export_to_json()`, `export_to_csv()`

### Data Flow

1. CLI parses arguments and loads credentials from env/prompts
2. InstagramClient logs in with session persistence
3. Fetches followers and following lists via private API
4. Computes set difference (following - followers)
5. Outputs results via selected formatter

## Development

### Setup
```bash
pip install -e .
```

### Running
```bash
# Direct module execution
python -m igcheck.cli

# Via installed entry point
igcheck
```

### Testing
Manual testing only for now (requires real Instagram credentials).

## Important Files

- `session.json` - Contains auth session (gitignored, sensitive)
- `.env` - Contains credentials (gitignored, sensitive)

## Dependencies

- `instagrapi` - Instagram private API client
- `click` - CLI framework
- `rich` - Console formatting
- `python-dotenv` - Environment variable loading

## Known Limitations

- Rate limiting from Instagram for large accounts
- Instagram may require challenge verification on new logins
- Session tokens expire after some time
