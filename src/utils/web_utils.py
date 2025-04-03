# src/utils/web_utils.py
from typing import Dict, Any
from playwright.async_api import async_playwright

class WebUtils:
    """Utility class for web interactions"""
    
    def __init__(self):
        self.browser = None
        self.page = None
        
    async def setup(self):
        """Setup browser"""
        if not self.browser:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=False)
            self.page = await self.browser.new_page()
            
    async def navigate(self, url: str):
        """Navigate to URL"""
        await self.setup()
        await self.page.goto(url)
        await self.page.wait_for_load_state("networkidle")
        
    async def search_portal(self, criteria: Dict[str, Any]) -> list:
        """Search CryoET portal with given criteria"""
        results = []
        
        try:
            # Find and use search input
            await self.page.fill('input[placeholder="Search..."]', 
                               criteria.get('protein_type', ''))
            await self.page.keyboard.press('Enter')
            await self.page.wait_for_load_state("networkidle")
            
            # Extract results
            dataset_cards = await self.page.query_selector_all('.dataset-card')
            for card in dataset_cards:
                title = await card.query_selector('.title')
                description = await card.query_selector('.description')
                
                results.append({
                    'title': await title.inner_text() if title else '',
                    'description': await description.inner_text() if description else ''
                })
                
        except Exception as e:
            print(f"Error during search: {e}")
            
        return results


    @staticmethod
    async def extract_dataset_info(page) -> List[Dict]:
        """Extract information from dataset cards"""
        datasets = []
        
        # Wait for dataset cards to be visible
        await page.wait_for_selector("td.css-1rkxiho")
        
        # Get all dataset cards
        cards = await page.query_selector_all("td.css-1rkxiho")
        
        for card in cards:
            # Extract link
            link_element = await card.query_selector("a[data-discover='true']")
            href = await link_element.get_attribute("href") if link_element else None
            
            # Extract image
            img_element = await card.query_selector("img[alt*='key visualization']")
            img_src = await img_element.get_attribute("src") if img_element else None
            
            datasets.append({
                "url": f"https://cryoetdataportal.czscience.com{href}" if href else None,
                "thumbnail": img_src,
                "id": href.split("/")[-1] if href else None
            })
            
        return datasets
        
    async def cleanup(self):
        """Cleanup browser resources"""
        if self.browser:
            await self.browser.close()
