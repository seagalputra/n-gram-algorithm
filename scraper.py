import bs4 as bs
import urllib.request
import re

def parse_sitemap(links):
    urls = []
    for link in links:
        sauce = urllib.request.urlopen(link).read()
        soup = bs.BeautifulSoup(sauce, 'xml')

        for url in soup.find_all('loc'):
            url_data = url.text.replace(' ', '').replace('\n', '')
            urls.append(url_data)
    
    return urls

def crawl_html(urls):
    for i in range(len(urls)):
        filename = 'article\detikcom'
        sauce = urllib.request.urlopen(urls[i]).read()
        soup = bs.BeautifulSoup(sauce, 'lxml')

        with open(filename+'\detik_'+str(i)+'.txt', 'w') as file:
            article = soup.find(id="detikdetailtext").text.replace("\n", "").replace("googletag.cmd.push(function() { googletag.display('div-gpt-ad-1546624523809-0'); });", " ").replace("<!--// <![CDATA[OA_show('newstag'); // ]]> --><!--// <![CDATA[OA_show('hiddenquiz'); // ]]> -->", "")
            file.write(article)
        
        print("Article %s scraped.." % i)

if __name__ == "__main__":

    # definisikan url yang akan di scraping
    links_sitemap = [
        'https://inet.detik.com/security/sitemap_web.xml',
        'https://inet.detik.com/telecommunication/sitemap_web.xml',
        'https://inet.detik.com/gadget/sitemap_web.xml'
    ]

    urls = parse_sitemap(links_sitemap)
    crawl_html(urls)