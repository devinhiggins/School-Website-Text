import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.loader import ItemLoader
from w3lib.html import remove_tags, remove_tags_with_content


class SchoolSpider(CrawlSpider):
    name = "school_spider"
    allowed_domains = ["acpsd.net"]
    start_urls = ["http://www.acpsd.net/AHS"]

    # this rule follows only links on the first level
    rules = (Rule(LinkExtractor(), callback="parse_page"),)

    # To follow all links from all pages change the rule to 'follow=True'
    # NOTE: From the test websites, this takes an extrememly long time to run.
    # rules = (Rule(LinkExtractor(), callback="parse_page", follow=True),)

    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "FEED_URI": "aiken_high_school_%(time)s.json",
        "FEED_FORMAT": "json",
    }

    def parse_page(self, response):
        # Attemp to extract only the BODY elements
        input = response.xpath("//body").extract()
        inputstr = "".join(input)
        # input = hxs.select('//div[@id="content"]').extract()
        # output = remove_tags(remove_tags_with_content(inputstr, ("script",)))
        scraped_info = {"page": response.url, "body": inputstr}

        yield scraped_info
