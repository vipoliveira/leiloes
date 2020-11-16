from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
import itertools
# Create your views here.

URL_BASE_SITE = "https://www.freitasleiloeiro.com.br"
URL_PATH_FIRST_SEARCH = "leiloes/pesquisar?pg=1&categoria=1"
URL_BASE_FIRST_SEARCH = "{}/{}".format(URL_BASE_SITE, URL_PATH_FIRST_SEARCH)

def search_ads(URL):

    freitas_return = requests.get(URL)
    ads_list = list()
    freitas_soup = BeautifulSoup(freitas_return.content, 'html5lib')

    cars_ad = freitas_soup.find("table", attrs={"id": "table_agendaX"}).findAll("tr", attrs={"class": "cursor-pointer"})
    errors = list()
    for car_ad in cars_ad:
        try:
            ads_list.append(
                {
                    'title': car_ad.find("h4").text.replace("""\n""", "").replace("  ", ""),
                    'ad_link': create_ad_link(car_ad),
                    'img_link': get_img_link(car_ad)
                }
            )
        except:
            errors.append(car_ad)
        # TODO log de erros
        #print(f"{len(errors)} errors found!")
    return ads_list

def discovery_page_last_path(URL_SEARCH):

    site_return = requests.get(URL_SEARCH)
    site_soup = BeautifulSoup(site_return.content, 'html5lib')
    try:
        last_button = site_soup.find(attrs={"class": "PagedList-skipToLast"}).findChild("a")
    except:
        last_button = site_soup.find(attrs={"class": "pagination-container"}).findAll("li")[-2].findChild("a")
    path = last_button.attrs['href']
    path = path.replace("&amp;", "&")

    return path

def create_ad_link(ad):

    ad_path = ad.find(attrs={"class": "btn btn-block btn-success"})
    path = ad_path.attrs['href']
    path = path.replace("&amp;", "&")
    ad_link = "{}/{}".format(URL_BASE_SITE, path)

    return ad_link

def get_img_link(ad):

    ad_img_block = ad.find(attrs={"class": "img-responsive", "id": "img-foto-destaque"})
    ad_img_link = ad_img_block.attrs['src']

    return ad_img_link

def pages_to_search(first_path):

    last_path = discovery_page_last_path(URL_BASE_FIRST_SEARCH)
    last_index = int(last_path.split("/")[-1].split("pg=")[-1].split("&")[0])
    first_index = int(first_path.split("/")[-1].split("pg=")[-1].split("&")[0])

    paths = []

    for index in range(first_index, last_index + 1):
        paths.append(f"leiloes/pesquisar?pg={index}&categoria=1")

    return paths

def fetch_all_ads():

    paths = pages_to_search(URL_PATH_FIRST_SEARCH)
    pages = [f"{URL_BASE_SITE}/{path}" for path in paths]
    ads = list()
    for page in pages:
        ads.append(search_ads(page))
    ads_nested = list(itertools.chain.from_iterable(ads))
    return ads_nested

def index(req):

    all_ads = fetch_all_ads()

    return render(req, 'my_app/index.html', {'ads': all_ads})