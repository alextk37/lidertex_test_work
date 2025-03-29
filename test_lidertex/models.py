from pydantic import BaseModel, conint, Field
from typing import List
from typing import Optional
from datetime import datetime

class Price(BaseModel):
    total: conint(ge=0)

class Size(BaseModel):
    price: Price

class Color(BaseModel):
    name: str

class Product(BaseModel):
    name: str
    reviewRating: float
    feedbacks: conint(ge=0)
    promoTextCard: Optional[str] = None
    totalQuantity: conint(ge=0)
    colors: List[Color]
    pics: conint(ge=0)
    sizes: List[Size]
    id: int

    def extract_data(self):
        return {
            "Название": self.name,
            "Рейтинг": self.reviewRating,
            "Количество отзывов": self.feedbacks,
            "Акция": self.promoTextCard or "Нет акции",
            "Цена (руб)": (self.sizes[0].price.total / 100) if self.sizes else 0.0,
            "Общий остаток": self.totalQuantity,
            "Количество цветов": len(self.colors),
            "Количество фото": self.pics,
            "WB": f"https://www.wildberries.ru/catalog/{self.id}/detail.aspx",
            "ID": self.id
        }

class Data(BaseModel):
    products: List[Product]

class Payload(BaseModel):
    data: Data

class SupplierData(BaseModel):
    id: conint(ge=0)
    valuation: str
    feedbacksCount: conint(ge=0)
    registrationDate: datetime
    saleItemQuantity: conint(ge=0)
    suppRatio: conint(ge=0, le=100)
    isPremium: bool

    def extract_data(self):
        return {
            "Ссылка на магазин": f'https://www.wildberries.ru/seller/{self.id}',
            "Средняя оценка": self.valuation,
            "Количество отзывов": self.feedbacksCount,
            "Дата регистрации": self.registrationDate.strftime('%Y-%m-%d'),
            "Общее количество продаж": self.saleItemQuantity,
            "Процент выкупа": self.suppRatio,
            "Джем": "Да" if self.isPremium else "Нет"
        }
    
class SupplierLegalInfo(BaseModel):
    supplierId: int = Field(..., alias="supplierId")
    supplierName: str = Field(..., alias="supplierName")
    supplierFullName: str = Field(..., alias="supplierFullName")
    inn: str = Field(..., alias="inn", pattern=r"^\d{10}$")
    ogrn: str = Field(..., alias="ogrn", pattern=r"^\d{13}$")
    legalAddress: str = Field(..., alias="legalAddress")
    trademark: str = Field(..., alias="trademark")
    kpp: str = Field(..., alias="kpp", pattern=r"^\d{9}$")
    taxpayerCode: str = Field(..., alias="taxpayerCode", pattern=r"^\d{10}$")
    unp: str | None = Field(None, alias="unp")
    bin: str | None = Field(None, alias="bin")
    unn: str | None = Field(None, alias="unn")

    def extract_data(self) -> dict:
        return {
            "Идентификатор": self.supplierId,
            "Краткое название": self.supplierName,
            "Полное название": self.supplierFullName,
            "ИНН": self.inn,
            "ОГРН": self.ogrn,
            "Юридический адрес": self.legalAddress,
            "Торговая марка": self.trademark,
            "КПП": self.kpp,
            "Код налогоплательщика": self.taxpayerCode,
        }