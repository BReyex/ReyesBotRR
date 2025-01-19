import asyncio
import json
from telegram import Bot
from telegram.request import HTTPXRequest
from telegram.error import TimedOut
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from funciones import login
import time

# Token del bot de Telegram y chat ID
TELEGRAM_TOKEN = '7799851520:AAGFBKCdhIhzzRTFhyTtAVm4hoF4nvUkpJI'
CHAT_ID = '-1002404336607'

# URL de la página
URL = "https://rivalregions.com/info/regions/5166"

# Archivo para almacenar los valores anteriores
DATA_FILE = "pop_data.json"

# Reintentar envío de mensajes
async def send_message_with_retries(bot, chat_id, message, retries=3, delay=5):
    for attempt in range(retries):
        try:
            await bot.send_message(chat_id=chat_id, text=message)
            return
        except TimedOut:
            if attempt < retries - 1:
                print(f"Reintento {attempt + 1}/{retries} tras error de tiempo de espera...")
                await asyncio.sleep(delay)
            else:
                print("Error: No se pudo enviar el mensaje después de varios intentos.")

# Notificar cambios
async def notify_changes(bot, old_data, new_data):
    for region, new_pop in new_data.items():
        old_pop = old_data.get(region, 0)
        if new_pop > old_pop:
            message = f"📈 La población de {region} aumentó de {old_pop} a {new_pop}."
            await send_message_with_retries(bot, CHAT_ID, message)
            await asyncio.sleep(1)

# Obtener contenido dinámico con Selenium
def get_dynamic_content(url):
    options = Options()
    options.add_argument('--headless')  # Ejecutar en modo sin cabeza
    options.add_argument('--no-sandbox')  # Desactivar el sandboxing
    options.add_argument('--disable-dev-shm-usage')  # Desactivar el uso de /dev/shm
    options.add_argument('--disable-gpu')  # Desactivar la aceleración de GPU
    options.add_argument('--window-size=1920x1080')  # Establecer el tamaño de la ventana
    options.add_argument('--start-maximized')  # Iniciar maximizado
    options.add_argument('--disable-extensions')  # Desactivar extensiones
    options.add_argument('--disable-infobars')  # Desactivar barras de información
        
    try:
        #add user Agent
        driver = uc.Chrome(options=options)
        url= "https://rivalregions.com"
        driver.get(url)
        time.sleep(5)
        login(driver, "aliyerlidemir06004@gmail.com", "gghTUPBX")
        #login(driver, "b.reyes.chavez@gmail.com", "i4nEamM4")
        time.sleep(5)  # Esperar a que el contenido se cargue
        driver.get(URL)
        time.sleep(5)  # Esperar a que se cargue la tabla
        html = driver.page_source
        return html
    finally:
        driver.quit()

# Cargar datos desde el archivo
def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Guardar datos en el archivo
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file)

# Extraer valores de la tabla
def scrape_pop_values():
    html = get_dynamic_content(URL)
    if not html:
        return {}

    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if table is None:
        print("No se encontró la tabla en la página.")
        return {}

    rows = table.find_all("tr")[1:]  # Omitir encabezado
    pop_data = {}
    for row in rows:
        columns = row.find_all("td")
        if len(columns) < 3:
            continue
        region_name = columns[0].text.strip()
        pop_value = int(columns[2].text.strip())
        pop_data[region_name] = pop_value
    return pop_data

# Función principal del bot
async def main():
    request = HTTPXRequest(connect_timeout=10, read_timeout=10)
    bot = Bot(token=TELEGRAM_TOKEN, request=request)
    old_data = load_data()

    while True:
        new_data = scrape_pop_values()
        if new_data:
            await notify_changes(bot, old_data, new_data)
            save_data(new_data)
            old_data = new_data
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
