import time
from datetime import datetime
from selenium.webdriver.common.by import By
from utils.driver import create_driver
from utils.file_manager import load_sent_products, save_product


def safe_find(card, by, value, attr=None, default=""):
    try:
        element = card.find_element(by, value)
        return element.get_attribute(attr) if attr else element.text
    except:
        return default


async def run_kabum_scraper(telegram_sender, url, csv_path):
    driver = create_driver()
    driver.get(url)

    sent, df = load_sent_products(csv_path)

    while True:
        product_cards = driver.find_elements(By.CLASS_NAME, "productCard")

        if not product_cards:
            print("[⚠️] Nenhum produto encontrado.")
            break

        for card in product_cards:
            name = safe_find(card, By.CLASS_NAME, "nameCard")
            if not name or name in sent:
                continue

            price = safe_find(card, By.CLASS_NAME, "priceCard")
            old_price = safe_find(card, By.CLASS_NAME, "oldPriceCard")
            discount = safe_find(card, By.CLASS_NAME, "bg-secondary-500")
            link = safe_find(card, By.CLASS_NAME, "productLink", attr="href")
            image = safe_find(card, By.CLASS_NAME, "imageCard", attr="src")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            try:
                await telegram_sender.send_product(name, discount, old_price, price, link, image)
                df = save_product(csv_path, df, {
                    'Nome': name,
                    'Preço': price,
                    'Preço Antigo': old_price,
                    'Desconto': discount,
                    'Link do Produto': link,
                    'Data': timestamp
                })
                time.sleep(1)
            except Exception as e:
                print(f"[❌ ERRO AO ENVIAR] {name}: {e}")
                continue

        try:
            next_button = driver.find_element(By.XPATH, '//*[@id="PaginationOffer"]/button')
            if not next_button.is_enabled():
                print("[ℹ️] Última página alcançada.")
                break
            next_button.click()
            time.sleep(3)
        except:
            print("[ℹ️] Botão de próxima página não encontrado.")
            break

    driver.quit()
