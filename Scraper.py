from pyppeteer import launch
import asyncio
from bs4 import BeautifulSoup

class Scraper():
    def __init__(self, festivalURL):
        self.browser = None
        self.festivalURL = festivalURL
        self.festivalID = None
        self.MAX_PAGE_REVIEWS = 2000
        self.nPage = 0
        self.totalRequest = 0
        self.requests = 0

    async def __slowRequest(self):
        self.totalRequest += 1
        self.requests += 1
        if self.requests >= 5:
            self.requests = 0
            await asyncio.sleep(3)
        else:
            await asyncio.sleep(0)
        

    async def start(self):
        try:
            self.browser = await launch(headless=False)
                
            page = await self.browser.newPage()
            r = await page.goto(self.festivalURL)
            await page.waitForSelector('body')
            await self.__slowRequest()
            festival_page = await page.content()
            
            if festival_page != "" and r.status == 200:
                soup_festivalPage = BeautifulSoup(festival_page, "html.parser")
                festival_link_tag = soup_festivalPage.find("section", id="reviews")

                if festival_link_tag != "":
                    if 'data-reviews-section' in festival_link_tag.attrs:
                        self.festivalID = festival_link_tag['data-reviews-section']

                        nPage = 1
                        while(nPage <= self.MAX_PAGE_REVIEWS):
                            page = await self.browser.newPage()
                            r = await page.goto(f"https://filmfreeway.com{self.festivalID}/reviews?page={nPage}")
                            await page.waitForSelector('body')
                            await self.__slowRequest()
                            reviewsHTML = await page.content()

                            if reviewsHTML != "" and r.status == 200:
                                soup_reviewsPage = BeautifulSoup(reviewsHTML, "html.parser")
                                reviews = soup_reviewsPage.find_all("div", class_="review-item__author")
                                print(reviews)
                            nPage = 2001


        except Exception as e:
            print(f"Si è verificato un errore durante l'accesso a {self.festivalURL}: {e}")
        finally:
            #await self.browser.close()
            ...

   
        
def main():
    s = Scraper("https://filmfreeway.com/INTERNATIONALMUSICFILMVIDEOFESTIVALURTIcanti")
    asyncio.run(s.start())


if __name__ == "__main__":
    main()