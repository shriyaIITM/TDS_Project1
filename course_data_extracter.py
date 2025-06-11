import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

class CourseDataRetriever:
  def __init__(self) -> None:
      pass

  async def get_links(self):
    links = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://tds.s-anand.net/#/")
        await page.wait_for_timeout(5000)  # wait for content to load

        # Get all anchor tags with hrefs
        a_tags = await page.eval_on_selector_all("a", "elements => elements.map(el => el.href)")

        # Filter unique links
        links = list(set(a_tags))
        await browser.close()

    return links

  async def filter_valid_links(self):
    links = await self.get_links()
    valid_links = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for link in links:
            try:
                await page.goto(link)
                await page.wait_for_timeout(2500)  # Wait for content to load

                # Get the visible page text
                content = await page.content()

                if "404" in content or "Page not found" in content:
                    print(f"❌ 404 Found: {link}")
                else:
                    print(f"✅ Valid: {link}")
                    valid_links.append(link)

            except Exception as e:
                print(f"⚠️ Error visiting {link}: {e}")

        await browser.close()

    return valid_links


  async def scrape_tds_pages(self):

    links = await self.filter_valid_links()
    scraped_data = {}  # link → extracted text

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for link in links:
            # 1) Only process internal SPA links (ignore external ones)
            if not link.startswith("https://tds.s-anand.net/#/"):
                print(f"⏭  Skipping external or root link: {link}")
                continue

            print(f"\n▶ Visiting: {link}")
            try:
                # Navigate and wait until network is idle
                await page.goto(link, wait_until="networkidle")
            except Exception as e:
                print(f"   ⚠️  Couldn’t load {link}: {e}")
                continue

            # Give the page a moment for late‐loading assets (images, XHR, etc.)
            await page.wait_for_timeout(3000)

            # 2) Grab the fully rendered HTML
            html = await page.content()

            # 3) Parse with BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")

            # a) Remove any <aside> (commonly used for sidebars)
            for aside in soup.find_all("aside"):
                aside.decompose()

            # b) Remove any element whose class contains "sidebar"
            for sidebar in soup.select("[class*=sidebar]"):
                sidebar.decompose()

            # c) Remove any docsify pagination containers
            for pag in soup.select(".docsify-pagination-container"):
                pag.decompose()

            # Try “<main>” first, then fallback to “<div id='app'>”, then full <body>
            container = (
                soup.select_one("main")
                or soup.select_one("div#app")
                or soup.body
            )

            # Get all remaining text (with newlines between blocks)
            text = container.get_text(separator="\n", strip=True)

            # Store in our dict
            scraped_data[link] = text

            # 6) (Optional) Print a short snippet for verification
            snippet = "\n".join(text.splitlines()[:5])
            print(f"   ✔ Snippet:\n{snippet}\n")

        await browser.close()

    return scraped_data



# if __name__ == "__main__":
#     cousedata = CourseDataRetriever()
#     data = await cousedata.scrape_tds_pages()
