from sqlalchemy import create_engine, Column, Integer, String, Numeric, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from datetime import datetime
from bs4 import BeautifulSoup
import requests

Base = declarative_base()
engine = create_engine("sqlite:///database.sqlite")
PRODUCT_URL = "https://www.perekrestok.ru"

class Price(Base):
    __tablename__ = "price"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    datetime = Column(DateTime)
    price = Column(String(64))
    price_float = Column(Numeric(10, 2))
    price_for_one = Column(String(64))
    url = Column(String)
    def __repr__(self):
        return f"{self.name}|{self.price}"
Base.metadata.create_all(engine)
session = Session(bind = engine)


def get_items (url):
    page = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(page.content, "lxml")
    href = soup.findAll(class_="sc-fFubgz fNiiPs sc-eCjkpP eSZnQC sc-kBPbqO hlKZLx")
    href = [PRODUCT_URL + (x.get('href')) for x in href]
    return href

def get_item(url):
    page = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(page.content, "lxml")
    products = soup.findAll(class_={"sc-fFubgz fsUTLG product-card__link", "product-card__title" , "price-new", "product-card__pricing"})
    for x in range(0, len(products), 4):
        url = products[x].get('href')
        price_for_one = products[x+1].get_text()
        title = products[x+2].get_text()
        price = products[x+3].get_text()
        price_float = price.split()
        price_float.pop()
        price_float = "".join(price_float).replace(',','.')
        price_float = float(price_float)
        is_exist = session.query(Price).filter(Price.name==title).order_by(Price.datetime.desc()).first()
        if not is_exist:
            session.add(Price(name=title, datetime=datetime.now(), price=price, price_float=price_float, price_for_one = price_for_one, url = PRODUCT_URL+url))
            session.commit()
        else:
            if is_exist.price_float != price_float:
                session.add(Price( name=title, datetime=datetime.now(), price=price, price_float=price_float, price_for_one = price_for_one, url = PRODUCT_URL+url))
                session.commit()

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    "user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0"
}
page = requests.get(url=PRODUCT_URL+'/cat', headers=headers)
soup = BeautifulSoup(page.content, "lxml")
items_groups = soup.findAll(class_="sc-fFubgz fsUTLG")
items_groups.pop(0)
items_groups.pop(0)
groups_url = [PRODUCT_URL + (x.get('href')) for x in items_groups]
groups = [get_items(x) for x in groups_url]
for items in groups:
    for item in items:
        get_item(item)