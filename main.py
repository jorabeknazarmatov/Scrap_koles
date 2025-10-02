from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from typing import List, Optional
import os, time
from conf import links
from log import logger
# from db import crud, engine
import models, re, json


class Parse:
    def __init__(self, links: List[str], headless: bool = True, default_timeout: int = 30_000):
        """
        links: список URL (например, список разделов каталога).
        headless: запуск без головы (True по умолчанию).
        default_timeout: таймаут операций Playwright в мс.
        """
        self.links = links
        self._p = sync_playwright().start()  # ВАЖНО: запускаем движок
        self.browser = self._p.chromium.launch(headless=headless)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.page.set_default_timeout(default_timeout)

    def _get_last_page(self, pagination_selector: str = ".pagination-page") -> int:
        """
        Определяет последнюю страницу пагинации.
        Ищем все элементы пагинации, извлекаем последное число.
        Если пагинации нет — возвращаем 1.
        """
        try:
            last_page = int(self.page.query_selector_all(pagination_selector)[-1].inner_text().strip())
        except PlaywrightTimeoutError:
            return 1

        if not last_page:
            return 1

        return last_page
       
    
    def page_r(self, pagination_selector: str = ".pagination-page") -> None:
        """
        Переходит на ссылку по индексу и печатает номера страниц от 1 до последней.
        Логику перехода по страницам (формирование URL) оставляем как TODO,
        т.к. она зависит от конкретного сайта.
        """
        
        if not self.links:
            raise ValueError("Список links пуст. Передайте хотя бы один URL.")

        for link in self.links:
            temp = []
            url = link
            # Ждём «networkidle», чтобы пагинация успела дорендериться (чаще всего надёжнее).
            self.page.goto(url, wait_until="networkidle")

            last = self._get_last_page(pagination_selector=pagination_selector)
            logger.info(f"{link} обнаружено {last} страниц")
            
            for page in range(1, 1 + 1):                
                next_url = f"{link}?page={page}"
                self.page.goto(next_url, wait_until="networkidle")
                cards = self.page.query_selector_all(".product-card__link")
                for card in cards:
                    temp.append(f"https://www.2000koles.ru{card.get_attribute('href')}")
                    logger.info(f"Страница: {page}, Линк: https://www.2000koles.ru{card.get_attribute('href')}")
            
            logger.info(f"В {link} обноружена {len(temp)} продуктов")
            
            for index, product_link in enumerate(temp, 1):
                logger.info(f"Начинаем парсит: {index}-продукт link:{product_link}")
                self.page.goto(product_link)
                
                # Забираем названия продукта 
                
                title = self.page.query_selector("h1").inner_text()
                logger.info(f"title: {title}")
                
                # Забираем url от img 
                
                image = self.page.query_selector(".swiper-slide img").get_attribute('src')
                logger.info(f"Фото url: {image}")
                
                # Забираем код продукта
                
                code = self.page.query_selector(".page-product__product-code span").inner_text()
                logger.info(f"Код продукта: {code}")
                
                # Забираем цену продукта
                
                price = int(re.sub(r"\D", "", self.page.query_selector(".left.prices-information .price").inner_text()))
                logger.info(f"Цена: {price}")
                                
                # Забираем описания продукта
                
                description = self.page.query_selector(".tab-content__body>div:nth-child(1)").text_content()
                logger.info(f"Описание: {description}")
                                
                # Забираем характеристику продукта
                
                key = self.page.query_selector_all(".tab-content__body>div:nth-child(2) .left")
                value = self.page.query_selector_all(".tab-content__body>div:nth-child(2) .right")
                
                temp_json = dict()
                
                for i, k in enumerate(key):
                    temp_json[k.text_content().split(":")[0].strip()] = value[i].inner_text().strip()
                
                # characteristic = json.dumps(temp_json, ensure_ascii=False, indent=2)
                characteristic = temp_json
                logger.info(f"Характеристика: {json.dumps(temp_json, ensure_ascii=False, indent=2)}")
                
                # Забираем наличие продукта
                
                self.page.click(".tab-content__head>div:nth-child(3)")
                time.sleep(1)
                self.page.wait_for_selector(".tab-content__body", timeout=10000)
                
                count = int(self.page.query_selector(".tab-content__body>div:nth-child(3) .right").inner_text().strip())
                logger.info(f"Наличие: {count}")
                
                # Проверяем есть ли у продукта кетегория Подходит к авто
                # если есть то спарсим их
                
                if self.page.query_selector(".tab-content__head>div:nth-child(4)").inner_text().strip() == "Подходит к авто":
                    self.page.click(".tab-content__head>div:nth-child(4)")
                    self.page.wait_for_selector(".tab-suitable-for-auto__table", timeout=10000)
                    
                    cars_table = self.page.query_selector_all(".tab-suitable-for-auto__table>table")
                    logger.info(f"Подходит к: {len(cars_table)} авто")
                    result = []
                    
                    tables = self.page.locator("table:has(thead th)").all()
                    for i, t in enumerate(tables):
                        brand = t.locator("thead th").first.inner_text().strip()

                        # Во вложенной таблице берём только строки данных (те, у которых есть <td>)
                        rows = t.locator("tbody td table tr:has(td)").all()
                        for r in rows:
                            model = r.locator("td").nth(0).inner_text().strip()

                            # Вторая ячейка содержит див со span-ами годов
                            years_cell_text = r.locator("td").nth(1).inner_text().strip()
                            # Извлекаем все четырёхзначные года, игнорируем запятые/пробелы
                            years = [int(y) for y in re.findall(r"\b\d{4}\b", years_cell_text)]

                            result.append({
                                "brand": brand,
                                "model": model,
                                "years": years,
                            })
                    
                    # suitabel_car = json.dumps(result, ensure_ascii=False, indent=2)
                    suitabel_car = result
                    logger.info(f"Спарсино {len(cars_table)} авто")
                else:
                    suitabel_car = None
                
                # if crud.find_product(code=code):
                #     continue
                # else:                    
                #     crud.add_product_with_info(
                #         name=title,
                #         image_url = image,
                #         code=code,
                #         price=price,
                #         count=count,
                #         characteristic=characteristic,
                #         description=description,
                #         suitable_car=suitabel_car
                #     )
                
                res = {
                    'name': title,
                    'image_url': image,
                    'code': code,
                    'price': price,
                    'count': count,
                    'characteristic': characteristic,
                    'description': description,
                    'suitable_car': suitabel_car
                }

                file_path = "data.json"

                # Если файл пустой или не существует, создаём список
                if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
                    data = []
                else:
                    with open(file_path, "r", encoding="utf-8") as file:
                        try:
                            data = json.load(file)
                        except json.JSONDecodeError:
                            data = []  # если файл повреждён или пустой

                # Добавляем новый объект
                data.append(res)

                # Перезаписываем уже обновлённый список
                with open(file_path, "w", encoding="utf-8") as file:
                    json.dump(data, file, ensure_ascii=False, indent=2)

                logger.info(f"Success: {index}-product")
                
                
                
    def close(self) -> None:
        """Корректно закрывает ресурсы Playwright."""
        try:
            if self.page:
                self.page.close()
        except Exception:
            pass
        try:
            if self.context:
                self.context.close()
        except Exception:
            pass
        try:
            if self.browser:
                self.browser.close()
        except Exception:
            pass
        try:
            if self._p:
                self._p.stop()
        except Exception:
            pass


if __name__ == "__main__":
    # models.Base.metadata.create_all(engine)
    parser = Parse(links=links, headless=True)
    try:
        parser.page_r(pagination_selector=".pagination-page")
    finally:
        parser.close()