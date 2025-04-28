# Gmail Scraping

## Google API's are a nightmare.

Upgraded gmail scraping from this useless repo: https://github.com/bozdoz/gmail-scraping

Used this quickstart: https://developers.google.com/gmail/api/quickstart/python#step_3_set_up_the_sample

Had to set up OAuth, add myself as a test user, run this script, continue through the security warnings, and allow access to my own data.  Service accounts don't work with gmail api, and token's don't seem to work well anymore either

!!
## YOU NEED TO DELETE token.json EVERY YEAR!
!!

## Usage

```bash
> NAMES="Mayor Quimby,Principal Skinner,Chief Wiggum" python main.py
 Mayor Quimby,12/1/2022,$675
 Principal Skinner,12/1/2022,$950
 Chief Wiggum,12/1/2022,$670
 ```