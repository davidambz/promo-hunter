import time
import asyncio
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        await asyncio.sleep(2)
        product_cards = driver.find_elements(By.CLASS_NAME, "productCard")

        if not product_cards:
            print("[⚠️] Nenhum produto encontrado.")
            break

        encontrou_novos = False

        for card in product_cards:
            name = safe_find(card, By.CLASS_NAME, "nameCard")
            if not name or name in sent:
                continue

            encontrou_novos = True

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
                sent.add(name)
                await asyncio.sleep(2)
            except Exception as e:
                print(f"[❌ ERRO AO ENVIAR] {name}: {e}")
                continue

        # Paginação segura via <li class="next"> > <a class="nextLink">
        try:
            wait = WebDriverWait(driver, 10)

            next_li = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "next"))
            )

            if "disabled" in next_li.get_attribute("class"):
                print("[ℹ️] Última página alcançada.")
                break

            next_link = next_li.find_element(By.CLASS_NAME, "nextLink")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_link)
            time.sleep(1)
            next_link.click()
            time.sleep(2)

        except Exception as e:
            print(f"[ℹ️] Não foi possível avançar para a próxima página: {e}")
            break

    driver.quit()
