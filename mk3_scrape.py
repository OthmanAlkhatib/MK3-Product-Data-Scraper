from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from requests import get
from time import sleep

options = ChromeOptions()
options.add_argument("--headless")
options.add_argument("--start-maximized")
options.add_argument("--log-level=3")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
chrome_prefs = dict()
chrome_prefs["profile.default_content_settings"] = {"images": 2}
chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
options.experimental_options["prefs"] = chrome_prefs

# Initialize Chrome Driver
driver = Chrome(ChromeDriverManager().install(), options=options)

def get_products_page_source(category):
    # Open Products Page
    driver.get("https://www.mk3.com/" + category)
    sleep(3)

    # Load All Products
    select_field = driver.find_element(By.ID, "items_per_page")
    select = Select(select_field)
    select.select_by_value("0")
    sleep(5)

    # Retrieve Page Source
    pg_src = driver.page_source

    return pg_src

def get_products_urls(html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        imgs = soup.find_all(class_="img-wrap")
        products_urls = []
        for img in imgs:
            products_urls.append("https://www.mk3.com" + img.a["href"])
        return products_urls
    except Exception as error:
        print("=== Error in get_products_urls ===")
        print(error)

def get_product_data(product_url):
    HEADERS = ({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US, en;q=0.5'
    })

    try:
        product_page_source = get(product_url,'html.parser', headers=HEADERS).content
        soup = BeautifulSoup(product_page_source, "html.parser")
    except Exception as error:
        print("==== Error : Can Not Get Page Source ====")
        print(error)
        return

    try:
        main_info_section = soup.select_one(".info-wrap2.col-12.col-md-6")
        title = main_info_section.h1.text
        price = main_info_section.find(class_="price2").text.strip().split(" ")[0].replace(",", "")
    except Exception as error:
        print("==== Error in title or price ====")
        print(error)
        title = "None"
        price = "None"

    try:
        images_section = soup.select_one(".img.col-12.col-md-6")
        imgs = []
        for div in images_section.find_all(class_="anchor") :
            imgs.append("https://www.mk3.com" + div.span["href"].replace("1000/1000", "999/999"))
        imgs_str = ', '.join(imgs)
    except Exception as error:
        print("==== Error in images ====")
        print(error)
        imgs_str = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTylVTVt1KVg4vewzVvkdujaEebnrPKxKimpA&usqp=CAU"

    try:
        description = str(soup.find("div", class_="mb-3"))\
            .replace("<html><body>", "")\
            .replace("</body></html>", "")\
            .replace('\n<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">\n', '')\
            .replace("\n", "")\
            .replace(",", "&")\
            .replace("href", "ref")\
            .replace('src="', 'src="https://www.mk3.com')
    except Exception as error:
        print("==== Error in Description ====")
        print(error)
        description = ""

    return title, price, imgs_str, description


if __name__ == "__main__":
    BRAND_SLUG = input("Enter Brand Slug : ")
    BRAND_CATEGORY = input("Enter Brand Category : ")
    MAIN_BRANDS = {BRAND_SLUG: BRAND_CATEGORY}

    for slug, cat in list(MAIN_BRANDS.items()):
        try:
            print(f"==== {cat} ====")
            pg_src = get_products_page_source(slug)
            print("== page source scraped ==")
            products_urls = get_products_urls(pg_src)
            print("== products urls scraped ==")
            file = open(f'{cat}.txt', 'w', encoding="utf-8")
            file.write('Name,"Regular price",Categories,Images,Description' + "\n")
            print("== file opened ==")
            print(str(len(products_urls)) + " Products Found..")
        except Exception as error :
            print(f"========== Error in Brand {cat} ==========")
            print(error)
            continue

        cnt = 0
        for product_url in products_urls :
            try:
                title, price, imgs_str, description = get_product_data(product_url)

                file.write(f'"{title}",')
                file.write(f'{price},')
                file.write(f'"{cat}",')
                file.write(f'"{imgs_str}",')
                file.write(f"'{description}'")
                file.write("\n")
                cnt += 1
                print(f"== product has been written {cnt} ==")
            except Exception as error:
                print(f"=== Error in Product {cnt} ===")
                print(error)
                cnt += 1
                continue
        file.close()
        print("")
        print("------------------------------------------------------------------------")
        print("")
    driver.quit()

