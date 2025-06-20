# gh_discussions_mass_enable
Programmatically enable Discussions for one or more (or --all) of a user's github repos via web browser (Playwright)

### Why
Because GH does not provide a REST API way to do this. I have found that using gh cli it can be done but haven't looked into how it does it if not via API. The Discussions GraphQL API seems to be only for managing discussions and the posts within it, not for enabling it on a repo.

### How
clone this repo.
```bash
pip install playwright
playwright install
python ghdiscen.py --user <userid> [--repos [list of repos] | --all]
```
### What
The script will launch a chromium browser to github.com. Signin with password (and 2FA) and sit back and watch.
