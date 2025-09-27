from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from conf import url
import models


engine = create_engine(url=url, connect_args={"options": "-c search_path=app,public"})

class DB_CRUD():
    def __init__(self):
        self.sessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    
    def find_product(self, code: str):
        
        with self.sessionLocal() as session:
            product = session.query(models.Product).filter_by(code=code).first()
            if not product:
                return None
            return product
    
    def add_product_with_info(
        self,
        *,
        name: str,
        code: str,
        price: int,
        image_url: str,
        count: int = 0,
        # manufacturer: str,
        description: str,
        characteristic: dict | None = None,
        suitable_car: dict | None = None,  # логичнее назваться suitable_car
    ) -> models.Product:
        """Создаёт Product и связанный Info за одну транзакцию и возвращает Product с подгруженным Info."""

        # безопасные дефолты вместо {} в сигнатуре
        characteristic = characteristic or {}
        suitable_car = suitable_car or {}

        with self.sessionLocal() as session:
            try:
                product = models.Product(
                    name=name,
                    code=code,
                    image_url=image_url,
                    price=price,
                    count=count,
                )

                info = models.Info(
                    # manufacturer=manufacturer,
                    description=description,
                    characteristic=characteristic,
                    suitabel_car=suitable_car,  # если переименуете поле — замените здесь
                )

                # привязать объект
                product.info = info

                session.add(product)
                session.commit()
                
                return f"{product.name} успешно записано в db"
            except Exception:
                session.rollback()
                raise

    def all_products(self):
        with self.sessionLocal() as session:
            products = session.query(models.Product).all()
            return [
                {
                    "id": p.id,
                    "name": p.name,
                    "code": p.code,
                    "price": p.price,
                    "count": p.count,
                    # "tagname": p.info.tagname,
                    # "manufacturer": p.info.manufacturer,
                    "description": p.info.description,
                    "characteristic": p.info.characteristic,
                    "suitabel_car": p.info.suitabel_car,
                    "created_at": p.created_at,
                }
                for p in products
            ]

crud = DB_CRUD()