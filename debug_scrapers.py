"""Debug individual scrapers"""
import asyncio
import httpx
from bs4 import BeautifulSoup
import warnings
import re
warnings.filterwarnings("ignore")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

async def test_bold_org():
    print("\n=== Testing Bold.org ===")
    async with httpx.AsyncClient(timeout=30, follow_redirects=True, headers=HEADERS) as client:
        r = await client.get("https://bold.org/scholarships/")
        print(f"Status: {r.status_code}")
        print(f"Content length: {len(r.text)}")
        
        soup = BeautifulSoup(r.text, 'lxml')
        
        # Find all links
        all_links = soup.find_all('a', href=True)
        print(f"Total links: {len(all_links)}")
        
        # Filter for scholarship links
        scholarship_links = []
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            if '/scholarships/' in href and text and len(text) > 10:
                scholarship_links.append((text[:50], href))
        
        print(f"Scholarship links: {len(scholarship_links)}")
        for t, h in scholarship_links[:5]:
            print(f"  - {t} -> {h}")

async def test_remotive():
    print("\n=== Testing Remotive ===")
    async with httpx.AsyncClient(timeout=30, follow_redirects=True, headers=HEADERS) as client:
        r = await client.get("https://remotive.com/api/remote-jobs?category=software-dev&limit=10")
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            jobs = data.get("jobs", [])
            print(f"Jobs: {len(jobs)}")
            if jobs:
                print(f"First job: {jobs[0].get('title')}")

async def main():
    await test_bold_org()
    await test_remotive()

if __name__ == "__main__":
    asyncio.run(main())
