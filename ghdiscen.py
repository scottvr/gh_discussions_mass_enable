
import asyncio
import argparse
from playwright.async_api import async_playwright

REPO_LIST_URL = "https://github.com/{user}?tab=repositories"

async def scrape_user_repos(page, username):
    print("🔍 Scraping repositories for user:", username)
    repos = []
    page_num = 1

    while True:
        url = REPO_LIST_URL.format(user=username) + f"&page={page_num}"
        await page.goto(url)
        await page.wait_for_selector("div#user-repositories-list ul", timeout=10000)

        repo_items = page.locator("div#user-repositories-list ul li h3 a")
        count = await repo_items.count()
        if count == 0:
            break

        for i in range(count):
            href = await repo_items.nth(i).get_attribute("href")
            if href and href.count("/") == 2 and not href.endswith("/settings"):
                repos.append(href.strip("/"))

        next_button = page.locator("a.next_page")
        if not await next_button.is_visible():
            break

        page_num += 1

    print(f"📦 Found {len(repos)} repos under {username}.")
    return repos

async def enable_discussions_on_repo(page, owner, repo):
    settings_url = f"https://github.com/{owner}/{repo}/settings#features"
    print(f"🔧 Navigating to settings for {owner}/{repo}...")
    await page.goto(settings_url)

    try:
        await page.wait_for_selector("input#discussions-feature", timeout=10000)
        checkbox = page.locator("input#discussions-feature")
        is_checked = await checkbox.is_checked()

        if is_checked:
            print(f"✅ Discussions already enabled for {owner}/{repo}")
            return

        await checkbox.check()
        print(f"☑️ Checked the Discussions box for {owner}/{repo}")
        await page.wait_for_timeout(1000)
        print(f"🎉 Enabled Discussions successfully for {owner}/{repo}")

    except Exception as e:
        print(f"❌ Failed to enable Discussions for {owner}/{repo}: {e}")

async def main(user, repos, use_all=False):
    if not user:
        print("❗ You must provide a GitHub username with --user.")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        print("🌐 Opening GitHub and waiting for login...")
        await page.goto("https://github.com")

        try:
            await page.wait_for_selector("img.avatar-user", timeout=180000)
            print("🔓 Login detected.")
        except:
            print("⏳ Login not detected after timeout. Exiting.")
            return

        if use_all:
            repos = await scrape_user_repos(page, user)
            if not repos:
                print("⚠️ No repos discovered. Aborting.")
                return
        else:
            repos = [f"{user}/{r}" if '/' not in r else r for r in repos]

        for repo in repos:
            owner, repo_name = repo.split('/')
            await enable_discussions_on_repo(page, owner, repo_name)
            await page.wait_for_timeout(1000)

        await browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enable GitHub Discussions on specified repos")
    parser.add_argument("--user", required=True, help="GitHub username to use for repo discovery or prefixing")
    parser.add_argument("--repos", nargs="+", help="List of repo names (or full owner/name)")
    parser.add_argument("--all", action="store_true", help="Enable on all repos under the given user")
    args = parser.parse_args()
    asyncio.run(main(args.user, args.repos or [], args.all))
