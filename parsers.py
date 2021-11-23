import requests
from bs4 import BeautifulSoup

HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
              ',application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/95.0.4638.69 Safari/537.36'
}


def olx(url):
    r = requests.get(url=url, headers=HEADERS)

    data = []

    soup = BeautifulSoup(r.text, 'lxml')
    item_cards = soup.find_all('div', class_='offer-wrapper')

    for item in item_cards:
        try:
            item_photo = item.find('td', class_='photo-cell').find('img').get('src')
        except AttributeError:
            item_photo = 'Нет фото'

        try:
            item_city = item.find('td', class_='bottom-cell').find('small', class_='breadcrumb x-normal').\
            find('span').text
        except AttributeError:
            item_city = 'Нет местоположения'

        try:
            item_title = item.find('h3', class_='lheight22 margintop5').text.strip()
        except AttributeError:
            item_title = 'Нет названия'

        try:
            item_price = item.find('p', class_='price').text.strip()
        except AttributeError:
            item_price = 'Нет цены'

        try:
            item_url = item.find('h3', class_='lheight22 margintop5').find('a').get('href')
        except AttributeError:
            item_url = 'Нет ссылки'

        data.append((item_photo, item_city, item_title, item_price, item_url))

    return data[5]


def auto_ria(url):
    r = requests.get(url=url, headers=HEADERS)

    data = []

    soup = BeautifulSoup(r.text, 'lxml')
    item_desk = soup.find('div', id='searchResults')
    another_item_desk = soup.find('div', class_='result-explore')

    if item_desk:
        item_cards = item_desk.find_all('section', class_='ticket-item')
        for item in item_cards:
            item_photo = item.find('picture').find('img').get('src')
            item_city = item.find('li', class_='view-location').text.replace('( от )', '').strip()
            item_title = item.find('div', class_='item ticket-title').find('a').text.strip()
            item_price = item.find('div', class_='price-ticket').find('span', class_='bold green size22').text
            item_url = item.find('div', class_='ticket-photo').find('a').get('href')

            data.append((item_photo, item_city, item_title, item_price, item_url))

    elif another_item_desk:
        another_item_cards = another_item_desk.find_all('section', class_='proposition')
        for another_item in another_item_cards:
            another_item_photo = another_item.find('picture').find('img').get('src')
            another_item_city = another_item.find('span', class_='item region').text.strip()
            another_item_title = another_item.find('h3', class_='proposition_name').find('span').text.strip()
            another_item_price = another_item.find('div', class_='proposition_price').find('span').text.strip()
            another_item_url = another_item.find('a').get('href')

            data.append((another_item_photo, another_item_city, another_item_title, another_item_price, another_item_url))

    return data[0]


if __name__ == '__main__':
    main()
