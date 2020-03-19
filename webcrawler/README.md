School Text Webcrawler
----------------------

The School Text project webscrawler is written in python and utilizes the Scrapy package.  It was written to be generic enough to crawl over multiple sites with varying HTML and scripting standards.

As such, the crawler includes the following features to assist in retrieving relevant text from each website:

- It only pulls from the <'BODY'> element of a webpage.  Removing the <'HEAD'> element helps eliminate much of the scripting code that resides on the pages.
- It will only crawl to a depth of 1.  Meaning that it will crawl to URLS contained on the main page, but stop crawling on URLs that appear on subsequent pages.    This is done to remove getting caught in a loop of crawling over pages it's already retrieved.
- It will only crawl on URLs referenced in the domain of the main page.  If a URL referenced exists on a different website or domain, that URL will be skipped.