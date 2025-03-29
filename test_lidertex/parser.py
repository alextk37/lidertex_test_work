import requests
import os
import json
from headers import (
    product_headers,
    product_params,
    vote_headers,
    vote_data,
    seller_info_headers,
    legal_info_headers
)
from models import Data, SupplierData, SupplierLegalInfo


class Parser:
    def __init__(self):
        self.product_headers = product_headers
        self.product_params = product_params
        self.vote_headers = vote_headers
        self.vote_data = vote_data
        self.seller_info_headers = seller_info_headers
        self.legal_info_headers = legal_info_headers

    def get_products(self):
        page = 1
        products = []
        while True:
            self.product_params['page'] = page
            response = requests.get(
                'https://catalog.wb.ru/brands/v2/catalog',
                params=self.product_params,
                headers=self.product_headers
            )

            # Проверяем статус ответа
            if response.status_code != 200:
                print(f"Ошибка {response.status_code}: {response.text}")
                break

            # Проверяем структуру и валидируем
            json_data = response.json()
            if 'data' not in json_data or 'products' not in json_data['data']:
                print("Ошибка: отсутствует data или products в ответе API")
                break

            data = Data.model_validate(json_data['data'])
            if not data.products:
                break
            
            products.extend(data.products)
            page += 1
    
        return [product.extract_data() for product in products]
    
    def get_votes(self):
        response = requests.post(
            'https://www.wildberries.ru/webapi/favorites/brand/getvotesbyid',
            headers=self.vote_headers,
            data=self.vote_data,
        )
        return response.json()['value']['votesCount']
    
    def get_seller_info(self):
        response = requests.get(
            'https://suppliers-shipment-2.wildberries.ru/api/v1/suppliers/4112047',
            headers=self.seller_info_headers,
        )

        if response.status_code != 200:
            raise Exception(f"Ошибка при получении данных. Код: {response.status_code}, Сообщение: {response.text}")

        try:
            data = SupplierData.model_validate(response.json())
            return data.extract_data()
        except Exception as e:
            raise Exception(f"Ошибка валидации данных: {e}")
    
    def get_legal_info(self):
        response = requests.get('https://static-basket-01.wbbasket.ru/vol0/data/supplier-by-id/4112047.json', 
                                headers=self.legal_info_headers)
        if response.status_code != 200:
            raise Exception(f"Ошибка при получении данных. Код: {response.status_code}, Сообщение: {response.text}")
        try:
            legal_data = SupplierLegalInfo.model_validate(response.json())
            return legal_data.extract_data()
        except Exception as e:
            raise Exception(f"Ошибка валидации данных: {e}")
        
    def get_local_json(self):
        file_path = os.path.join("local_data", "local_data.json")

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return data
        

    def get_combined_data(self):
        json_data_1 = self.get_products()
        json_data_2 = self.get_local_json()

        combined_data = []

        sku_dict = {product['SKU']: product for product in json_data_2}

        for product_1 in json_data_1:
            product_id = product_1.get('ID')

            # Если товар из первого JSON есть во втором JSON (по SKU)
            if product_id in sku_dict:
                # Получаем товар из второго JSON по SKU
                product_2 = sku_dict[product_id]

                # Объединяем данные из обоих JSON
                combined_product = {
                    'Название': product_1['Название'],
                    'Рейтинг': product_1['Рейтинг'],
                    'Количество отзывов': product_1['Количество отзывов'],
                    'Акция': product_1['Акция'],
                    'Цена (руб)': product_1['Цена (руб)'],
                    'Общий остаток': product_1['Общий остаток'],
                    'Количество цветов': product_1['Количество цветов'],
                    'Количество фото': product_1['Количество фото'],
                    'WB': product_1['WB'],
                    'ID': product_1['ID'],
                    'SKU': product_2['SKU'],
                    'Выручка, ₽': product_2['Выручка, ₽'],
                    'Упущенная выручка, ₽': product_2['Упущенная выручка, ₽'],
                    'Продажи, кол-во': product_2['Продажи, кол-во'],
                    'График продаж': product_2['График продаж'],
                    'Оборачиваемость, дн.': product_2['Оборачиваемость, дн.'],
                    'График остатков': product_2['График остатков'],
                    'Скидка': product_2['Скидка'],
                    'График изменения цены': product_2['График изменения цены'],
                    'Дробный рейтинг': product_2['Дробный рейтинг'],
                    'Ср. рейтинг последних отзывов': product_2['Ср. рейтинг последних отзывов'],
                    'Дней на маркетплейсе': product_2['Дней на маркетплейсе'],
                    'Средняя рекламная ставка, ₽': product_2['Средняя рекламная ставка, ₽']
                }
                combined_data.append(combined_product)
        
        return combined_data
