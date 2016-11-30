from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urlparse
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
    parsed_uri = urlparse(url)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
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
            caminho = "links/static/images/"
            try:
                urllib.request.urlretrieve(each,"%s"%(caminho)+str(link_slug)+filename)
                downloaded = True
            except Exception:
                try:
                    aux = domain + each
                    urllib.request.urlretrieve(aux,"%s"%(caminho)+str(link_slug)+filename)
                    downloaded = True
                except Exception as e:
                    try:
                        aux2 = url[0:url.index('/',8)] + each
                        urllib.request.urlretrieve(aux2,"%s"%(caminho)+str(link_slug)+filename)
                        downloaded = True
                    except Exception as e:
                        try:
                            aux3 = 'http:' + each
                            urllib.request.urlretrieve(aux3,"%s"%(caminho)+str(link_slug)+filename)
                            downloaded = True
                        except Exception as e:
                            continue
    return filename,downloaded
