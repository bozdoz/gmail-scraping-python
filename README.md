# Gmail Scraping

## Google API's are a nightmare.

Used this quickstart: https://developers.google.com/gmail/api/quickstart/python#step_3_set_up_the_sample

## Getting Started

1. Get credentials.json (from https://console.cloud.google.com/auth/clients)

2. Run in Docker (dev container)

3. Install deps (`pip-sync`)

4. Run QuickStart (`python quickstart.py`)

You should now have `token.json` in the project.

## Usage

> [!IMPORTANT]
> Make sure there are spaces!

```bash
> NAMES="Mayor Quimby, Principal Skinner, Chief Wiggum" python main.py
 Mayor Quimby,12/1/2022,$675
 Principal Skinner,12/1/2022,$950
 Chief Wiggum,12/1/2022,$670
 ```

## Other Info

Upgraded gmail scraping from this useless repo: https://github.com/bozdoz/gmail-scraping

Had to set up OAuth, add myself as a test user, run this script, continue through the security warnings, and allow access to my own data.  Service accounts don't work with gmail api, and token's don't seem to work well anymore either

> [!IMPORTANT]
> YOU NEED TO DELETE token.json EVERY YEAR!
