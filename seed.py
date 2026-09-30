from sqlmodel import Session, select
from datetime import date, timedelta
from main import engine, Member, create_db_and_tables

def seed():
    create_db_and_tables()

    with Session(engine) as session:
        # Evitar duplicar datos si ya existen
        existentes = session.exec(select(Member)).first()
        if existentes:
            print("La base ya tiene datos. No se cargó nada.")
            return

        miembros = [
            Member(
                name="Juan",
                surname="Pérez",
                email="juan.perez@email.com",
                phone_number="1122334455",
                plan="mensual",
                start_date=date.today() - timedelta(days=10),
                end_date=date.today() + timedelta(days=20),
                status="active",
                dni="30111222"
            ),
            Member(
                name="María",
                surname="Gómez",
                email="maria.gomez@email.com",
                phone_number="1133445566",
                plan="trimestral",
                start_date=date.today() - timedelta(days=30),
                end_date=date.today() + timedelta(days=60),
                status="active",
                dni="28444555"
            ),
            Member(
                name="Carlos",
                surname="López",
                email="carlos.lopez@email.com",
                phone_number="1144556677",
                plan="anual",
                start_date=date.today() - timedelta(days=100),
                end_date=date.today() + timedelta(days=265),
                status="active",
                dni="25666777"
            ),
            Member(
                name="Ana",
                surname="Rodríguez",
                email="ana.rodriguez@email.com",
                phone_number="1155667788",
                plan="mensual",
                start_date=date.today() - timedelta(days=45),
                end_date=date.today() - timedelta(days=15),  # vencido
                status="expired",
                dni="31222333"
            ),
            Member(
                name="Lucas",
                surname="Fernández",
                email="lucas.fernandez@email.com",
                phone_number="1166778899",
                plan="trimestral",
                start_date=date.today() - timedelta(days=20),
                end_date=date.today() + timedelta(days=70),
                status="active",
                dni="29888999"
            ),
            Member(
                name="Sofía",
                surname="Martínez",
                email="sofia.martinez@email.com",
                phone_number="1177889900",
                plan="mensual",
                start_date=date.today() - timedelta(days=5),
                end_date=date.today() + timedelta(days=25),
                status="inactive",
                dni="32333444"
            ),
        ]

        for m in miembros:
            session.add(m)

        session.commit()
        print(f"Se cargaron {len(miembros)} miembros de prueba.")

if __name__ == "__main__":
    seed()