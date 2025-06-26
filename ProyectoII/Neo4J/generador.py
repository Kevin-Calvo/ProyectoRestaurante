import csv
import random
from datetime import datetime, timedelta

NUM_USUARIOS = 500
NUM_RESTAURANTES = 50
NUM_UBICACIONES = 100
NUM_PRODUCTOS = 100
NUM_PEDIDOS = 1000
RELACIONES_REQUERIDAS = 3000

random.seed(42)

# --- usuarios.csv
with open("usuarios.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["id", "nombre"])
    for i in range(1, NUM_USUARIOS + 1):
        writer.writerow([i, f"Usuario{i}"])

# --- restaurantes.csv
with open("restaurantes.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["id", "nombre"])
    for i in range(1, NUM_RESTAURANTES + 1):
        writer.writerow([i, f"Restaurante{i}"])

# --- ubicaciones.csv
with open("ubicaciones.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["id", "nombre", "lat", "lon"])
    for i in range(1, NUM_UBICACIONES + 1):
        lat = round(9.9 + random.uniform(-0.2, 0.2), 6)
        lon = round(-84.1 + random.uniform(-0.2, 0.2), 6)
        writer.writerow([i, f"Ubicacion{i}", lat, lon])

# --- productos.csv
with open("productos.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["id", "nombre"])
    for i in range(1, NUM_PRODUCTOS + 1):
        writer.writerow([i, f"Producto{i}"])

# --- pedidos.csv
with open("pedidos.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["id", "dia", "hora"])
    base_date = datetime(2025, 1, 1)
    for i in range(1, NUM_PEDIDOS + 1):
        day_offset = random.randint(0, 180)
        time_val = datetime(2025, 1, 1, random.randint(10, 22), random.choice([0, 15, 30, 45]))
        writer.writerow([i, (base_date + timedelta(days=day_offset)).date(), time_val.time()])

# --- relaciones.csv
with open("relaciones.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["desde_tipo", "desde_id", "relacion", "hasta_tipo", "hasta_id"])

    count = 0

    # RELIZA (Usuario -> Pedido)
    for i in range(1, NUM_PEDIDOS + 1):
        uid = random.randint(1, NUM_USUARIOS)
        writer.writerow(["Usuario", uid, "REALIZA", "Pedido", i])
        count += 1

    # PERTENECE_A (Pedido -> Restaurante)
    for i in range(1, NUM_PEDIDOS + 1):
        rid = random.randint(1, NUM_RESTAURANTES)
        writer.writerow(["Pedido", i, "PERTENECE_A", "Restaurante", rid])
        count += 1

    # ENTREGADO_EN (Pedido -> Ubicacion)
    for i in range(1, NUM_PEDIDOS + 1):
        lid = random.randint(1, NUM_UBICACIONES)
        writer.writerow(["Pedido", i, "ENTREGADO_EN", "Ubicacion", lid])
        count += 1

    # CONTINE (Pedido -> Producto)
    for i in range(1, NUM_PEDIDOS + 1):
        productos = random.sample(range(1, NUM_PRODUCTOS + 1), random.randint(1, 3))
        for pid in productos:
            writer.writerow(["Pedido", i, "CONTINE", "Producto", pid])
            count += 1

    # RECOMIENDA (Usuario -> Restaurante)
    for _ in range(600):
        uid = random.randint(1, NUM_USUARIOS)
        rid = random.randint(1, NUM_RESTAURANTES)
        writer.writerow(["Usuario", uid, "RECOMIENDA", "Restaurante", rid])
        count += 1

    # SIGUIENDO_A (Usuario -> Usuario)
    for _ in range(600):
        a, b = random.sample(range(1, NUM_USUARIOS + 1), 2)
        writer.writerow(["Usuario", a, "SIGUIENDO_A", "Usuario", b])
        count += 1

    print(f"Total relaciones generadas: {count}")
