from bs4 import BeautifulSoup
from urllib.request import urlopen
import urllib.request

def make_soup(url):
    try:
        html = urlopen(url).read()
        return BeautifulSoup(html,"lxml")

    except urllib.error.HTTPError as e:
        return "Use default image"

def get_images(url,slug):
    downloaded = False
    try:
        soup = make_soup(url)
    except:
        return("Use default image",downloaded)
    if soup == None or type(soup) == str:
        return ("Use default image",downloaded)
    images = [img for img in soup.findAll('img')]
    image_links = [each.get('src') for each in images]
    link_slug = slug
    filename = ''
    for each in image_links:
        if downloaded:
            break
        booleano = False
        if each != "":
            if each == None:
                continue
            if 'jpg' in each:
                booleano = True
                pos = each.index("jpg")
                each = each[0:pos+3]
                filename = '.jpg'
            elif 'png' in each:
                booleano = True
                pos = each.index("png")
                each = each[0:pos+3]
                filename = '.png'
            elif 'jpeg' in each:
                booleano = True
                pos = each.index('jpeg')
                each = each[0:pos+4]
                filename = '.jpeg'
            if not booleano:
                continue

            if each[0] + each[1] == '//' or each[0] == '/':
                each = 'http:'+each
            if each[0:4] != 'http' and each[0:5] != 'https':
                each = url[0:url.index('/',8)] + each
            caminho = "links/static/images/"
            try:
                urllib.request.urlretrieve(each,"%s"%(caminho)+str(link_slug)+filename)
                downloaded = True
            except Exception:
                continue
    return filename,downloaded
