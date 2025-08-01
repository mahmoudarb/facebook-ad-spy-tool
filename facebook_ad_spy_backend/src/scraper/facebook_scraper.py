import asyncio
import re
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FacebookAdsScraper:
    def __init__(self):
        self.base_url = "https://www.facebook.com/ads/library/"
        self.ads_data = []
        
    async def scrape_page_ads(self, page_id, max_ads=None):
        """
        Scrape all ads for a given Facebook page ID
        
        Args:
            page_id (str): Facebook page ID
            max_ads (int, optional): Maximum number of ads to scrape
            
        Returns:
            dict: Contains page_name, page_id, and list of ads
        """
        url = f"{self.base_url}?active_status=all&ad_type=all&country=ALL&view_all_page_id={page_id}"
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            page = await context.new_page()
            
            try:
                logger.info(f"Navigating to Facebook Ads Library for page ID: {page_id}")
                await page.goto(url, wait_until="networkidle", timeout=30000)
                
                # Wait for the page to load
                await page.wait_for_timeout(3000)
                
                # Check if there are any ads
                no_ads_selector = "text=No ads match your search criteria"
                try:
                    await page.wait_for_selector(no_ads_selector, timeout=5000)
                    logger.info(f"No ads found for page ID: {page_id}")
                    return {
                        'page_id': page_id,
                        'page_name': None,
                        'ads': [],
                        'error': 'No ads found'
                    }
                except PlaywrightTimeoutError:
                    # Ads are present, continue scraping
                    pass
                
                # Get page name
                page_name = await self._extract_page_name(page)
                logger.info(f"Found page: {page_name}")
                
                # Scroll and collect ads
                ads = await self._scroll_and_collect_ads(page, max_ads)
                
                logger.info(f"Scraped {len(ads)} ads for page: {page_name}")
                
                return {
                    'page_id': page_id,
                    'page_name': page_name,
                    'ads': ads,
                    'error': None
                }
                
            except Exception as e:
                logger.error(f"Error scraping page {page_id}: {str(e)}")
                return {
                    'page_id': page_id,
                    'page_name': None,
                    'ads': [],
                    'error': str(e)
                }
            finally:
                await browser.close()
    
    async def _extract_page_name(self, page):
        """Extract the page name from the ads library page"""
        try:
            # Look for the page name in various possible selectors
            selectors = [
                'h1',
                '[data-testid="page-name"]',
                'a[href*="/ads/library/"] span',
                'div[role="heading"]'
            ]
            
            for selector in selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=2000)
                    if element:
                        text = await element.inner_text()
                        if text and len(text.strip()) > 0:
                            return text.strip()
                except:
                    continue
            
            # Fallback: try to extract from URL or page content
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Look for any element containing the page name
            page_links = soup.find_all('a', href=True)
            for link in page_links:
                if 'facebook.com' in link.get('href', '') and link.text.strip():
                    return link.text.strip()
            
            return "Unknown Page"
            
        except Exception as e:
            logger.warning(f"Could not extract page name: {str(e)}")
            return "Unknown Page"
    
    async def _scroll_and_collect_ads(self, page, max_ads=None):
        """Scroll through the page and collect all ad data"""
        ads = []
        last_ad_count = 0
        no_new_ads_count = 0
        max_scrolls = 50  # Prevent infinite scrolling
        scroll_count = 0
        
        while scroll_count < max_scrolls:
            # Extract ads from current viewport
            current_ads = await self._extract_ads_from_page(page)
            
            # Add new ads (avoid duplicates by library_id)
            existing_library_ids = {ad['library_id'] for ad in ads}
            new_ads = [ad for ad in current_ads if ad['library_id'] not in existing_library_ids]
            ads.extend(new_ads)
            
            logger.info(f"Scroll {scroll_count + 1}: Found {len(new_ads)} new ads, total: {len(ads)}")
            
            # Check if we've reached the maximum
            if max_ads and len(ads) >= max_ads:
                ads = ads[:max_ads]
                break
            
            # Check if we're getting new ads
            if len(ads) == last_ad_count:
                no_new_ads_count += 1
                if no_new_ads_count >= 3:  # Stop if no new ads for 3 scrolls
                    logger.info("No new ads found after 3 scrolls, stopping")
                    break
            else:
                no_new_ads_count = 0
                last_ad_count = len(ads)
            
            # Scroll down
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)  # Wait for new content to load
            
            scroll_count += 1
        
        return ads
    
    async def _extract_ads_from_page(self, page):
        """Extract ad data from the current page content"""
        ads = []
        
        try:
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find ad containers - these may vary based on Facebook's current structure
            ad_containers = soup.find_all('div', {'role': 'article'}) or \
                           soup.find_all('div', class_=re.compile(r'.*ad.*', re.I)) or \
                           soup.find_all('div', attrs={'data-testid': re.compile(r'.*ad.*', re.I)})
            
            if not ad_containers:
                # Fallback: look for any div containing "Library ID"
                ad_containers = soup.find_all('div', string=re.compile(r'Library ID', re.I))
                ad_containers = [container.find_parent('div') for container in ad_containers if container.find_parent('div')]
            
            for container in ad_containers:
                ad_data = self._extract_ad_data_from_container(container)
                if ad_data and ad_data['library_id']:
                    ads.append(ad_data)
            
            # Remove duplicates based on library_id
            seen_ids = set()
            unique_ads = []
            for ad in ads:
                if ad['library_id'] not in seen_ids:
                    seen_ids.add(ad['library_id'])
                    unique_ads.append(ad)
            
            return unique_ads
            
        except Exception as e:
            logger.error(f"Error extracting ads from page: {str(e)}")
            return []
    
    def _extract_ad_data_from_container(self, container):
        """Extract individual ad data from a container element"""
        try:
            ad_data = {
                'library_id': None,
                'ad_text': None,
                'media_url': None,
                'media_type': None,
                'start_date': None,
                'platforms': [],
                'cta': None
            }
            
            # Extract Library ID
            library_id_text = container.find(string=re.compile(r'Library ID:?\s*(\d+)', re.I))
            if library_id_text:
                match = re.search(r'Library ID:?\s*(\d+)', library_id_text, re.I)
                if match:
                    ad_data['library_id'] = match.group(1)
            
            # Extract ad text
            text_elements = container.find_all(['p', 'div', 'span'], string=True)
            for element in text_elements:
                text = element.get_text(strip=True)
                if text and len(text) > 20 and 'Library ID' not in text and 'Started running' not in text:
                    ad_data['ad_text'] = text
                    break
            
            # Extract start date
            date_text = container.find(string=re.compile(r'Started running on', re.I))
            if date_text:
                match = re.search(r'Started running on\s+([A-Za-z]+\s+\d+,\s+\d+)', date_text, re.I)
                if match:
                    try:
                        date_str = match.group(1)
                        ad_data['start_date'] = datetime.strptime(date_str, '%b %d, %Y').date()
                    except ValueError:
                        pass
            
            # Extract media URL
            img_tags = container.find_all('img', src=True)
            video_tags = container.find_all('video', src=True)
            
            if img_tags:
                # Find the largest image (likely the ad creative)
                largest_img = max(img_tags, key=lambda img: len(img.get('src', '')))
                ad_data['media_url'] = largest_img.get('src')
                ad_data['media_type'] = 'image'
            elif video_tags:
                ad_data['media_url'] = video_tags[0].get('src')
                ad_data['media_type'] = 'video'
            
            # Extract platforms
            platform_text = container.find(string=re.compile(r'Platforms?', re.I))
            if platform_text:
                # Look for platform indicators
                if 'Facebook' in str(container):
                    ad_data['platforms'].append('Facebook')
                if 'Instagram' in str(container):
                    ad_data['platforms'].append('Instagram')
            
            # Extract CTA (Call to Action) - look for common CTA patterns
            cta_patterns = [
                r'(Learn More|Shop Now|Sign Up|Download|Get Started|Book Now|Call Now|Contact Us|Visit Website)',
                r'(Mehr erfahren|Jetzt kaufen|Registrieren|Herunterladen)',  # German
                r'(En savoir plus|Acheter maintenant|S\'inscrire|Télécharger)'  # French
            ]
            
            for pattern in cta_patterns:
                cta_match = container.find(string=re.compile(pattern, re.I))
                if cta_match:
                    match = re.search(pattern, cta_match, re.I)
                    if match:
                        ad_data['cta'] = match.group(1)
                        break
            
            return ad_data if ad_data['library_id'] else None
            
        except Exception as e:
            logger.error(f"Error extracting ad data from container: {str(e)}")
            return None

# Async function to run the scraper
async def scrape_facebook_ads(page_ids, max_ads_per_page=None):
    """
    Scrape ads for multiple Facebook page IDs
    
    Args:
        page_ids (list): List of Facebook page IDs
        max_ads_per_page (int, optional): Maximum ads per page
        
    Returns:
        list: List of page data with ads
    """
    scraper = FacebookAdsScraper()
    results = []
    
    for page_id in page_ids:
        try:
            result = await scraper.scrape_page_ads(page_id, max_ads_per_page)
            results.append(result)
            
            # Add delay between pages to avoid rate limiting
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"Error scraping page {page_id}: {str(e)}")
            results.append({
                'page_id': page_id,
                'page_name': None,
                'ads': [],
                'error': str(e)
            })
    
    return results

