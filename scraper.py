import bs4 as bs
import urllib.request
import re

def parse_sitemap(links):
    '''
    Fungsi untuk melakukan parsing sitemap.xml yang ada pada suatu situs
    
    Input : Website sitemap.xml
    Ouput : Url yang terdapat pada sitemap
    '''

    urls = []
    for link in links:
        sauce = urllib.request.urlopen(link).read()
        soup = bs.BeautifulSoup(sauce, 'xml')

        for url in soup.find_all('loc'):
            url_data = url.text.replace(' ', '').replace('\n', '')
            urls.append(url_data)
    
    return urls

def crawl_html(urls):
    '''
    Fungsi untuk melakukan crawling pada suatu situs dan mengambil file html
    yang nantinya dilakukan parsing pada html tersebut

    Input : Url yang diakan diparsing
    Output : File txt hasil parsing
    '''
    for i in range(len(urls)):
        filename = 'article\detikcom'
        sauce = urllib.request.urlopen(urls[i]).read()
        soup = bs.BeautifulSoup(sauce, 'lxml')

        with open(filename+'\detik_'+str(i)+'.txt', 'w') as file:
            article = soup.find(id="detikdetailtext").text.replace("\n", "").replace("googletag.cmd.push(function() { googletag.display('div-gpt-ad-1546624523809-0'); });", " ").replace("<!--// <![CDATA[OA_show('newstag'); // ]]> --><!--// <![CDATA[OA_show('hiddenquiz'); // ]]> -->", "")
            file.write(article)
        
        print("Article %s scraped.." % i)

def main():
    # definisikan url yang akan di scraping
    links_sitemap = [
        'https://inet.detik.com/security/sitemap_web.xml',
        'https://inet.detik.com/telecommunication/sitemap_web.xml',
        'https://inet.detik.com/gadget/sitemap_web.xml'
    ]

    urls = parse_sitemap(links_sitemap)
    crawl_html(urls)

if __name__ == "__main__":
    main()