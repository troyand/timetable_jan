from selenium import webdriver
from selenium.webdriver.common.by import By



def crawl(browser, visited, url, prefix):
    sanitized_url = url.split('?')[0].split('#')[0]
    if '/rooms-status/' in url:
        url = prefix + 'rooms-status/2012/1/10/'
        sanitized_url = url
    if sanitized_url in visited:
        return
    if not url.startswith(prefix):
        return
    if '/week/' in url or '/group/' in url:
        return
    if '/ical/' in url:
        return
    browser.get(url)
    screensot_filename = sanitized_url.replace(prefix, '').replace('/', '_')[:-1]
    if not screensot_filename:
        screensot_filename = 'index'
    screensot_filename = 'blackbox_tests/screenshots/%s.png' % screensot_filename
    browser.save_screenshot(screensot_filename)
    visited.add(sanitized_url)
    links = browser.find_elements(By.TAG_NAME, "a")
    hrefs = [link.get_attribute('href') for link in links]
    for href in hrefs:
        crawl(browser, visited, href, prefix)

browser = webdriver.Firefox()
visited = set()
crawl(browser, visited, 'http://localhost:8000/', prefix='http://localhost:8000/')
browser.close()

