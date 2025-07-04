import requests
from bs4 import BeautifulSoup
import json

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

BASE_URL = 'https://www.olx.uz/kattakurgan/'

def fetch_page(url):
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.text

def parse_ads(html):
    soup = BeautifulSoup(html, 'html.parser')
    ads = []
    for item in soup.select('div[data-cy="l-card"]'):
        title = item.select_one('h6').get_text(strip=True) if item.select_one('h6') else ''
        price = item.select_one('p[data-testid="ad-price"]').get_text(strip=True) if item.select_one('p[data-testid="ad-price"]') else ''
        location = item.select_one('p[data-testid="location-date"]').get_text(strip=True) if item.select_one('p[data-testid="location-date"]') else ''
        link = item.select_one('a')['href'] if item.select_one('a') else ''
        if link and not link.startswith('http'):
            link = 'https://www.olx.uz' + link
        image = item.select_one('img')
        image_url = image['src'] if image and image.has_attr('src') else ''
        # Faqat Kattaqo‘rg‘on e'lonlari uchun filter
        if 'Каттакурган' in location or 'Kattaqo‘rg‘on' in location:
            # Batafsil ma'lumotlarni olish uchun e'lon sahifasini ochamiz
            details = fetch_ad_details(link) if link else {}
            ad = {
                'title': title,
                'price': price,
                'location': location,
                'link': link,
                'image': image_url
            }
            ad.update(details)
            ads.append(ad)
    return ads

# Har bir e'lon sahifasidan batafsil ma'lumotlarni olish
def fetch_ad_details(link):
    try:
        html = fetch_page(link)
        soup = BeautifulSoup(html, 'html.parser')
        # E'lon tavsifi
        description = ''
        desc_tag = soup.select_one('div[data-cy="ad_description"]')
        if desc_tag:
            description = desc_tag.get_text(strip=True)

        # Barcha rasm URLlarini olish
        image_urls = []
        # OLX sahifasida barcha rasm <img> larini topamiz (asosiy galereya uchun)
        gallery = soup.select('div[data-testid="gallery-container"] img')
        for img in gallery:
            if img.has_attr('src'):
                image_urls.append(img['src'])
        # Agar yuqoridagi topilmasa, boshqa <img> larni ham tekshirib ko'ramiz
        if not image_urls:
            for img in soup.find_all('img'):
                if img.has_attr('src') and 'olxcdn.com' in img['src']:
                    image_urls.append(img['src'])

        return {
            'description': description,
            'images': image_urls
        }
    except Exception as e:
        return {'description': f'Error: {e}', 'images': []}

def main():
    html = fetch_page(BASE_URL)
    ads = parse_ads(html)
    # Natijani JSON faylga yozamiz
    with open('olx_kattakurgan_ads2.json', 'w', encoding='utf-8') as f:
        json.dump(ads, f, ensure_ascii=False, indent=2)
    print(f"{len(ads)} ta e'lon json faylga yozildi: olx_kattakurgan_ads.json")

if __name__ == "__main__":
    main()
