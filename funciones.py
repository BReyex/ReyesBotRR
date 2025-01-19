from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def login(driver, username, password):
    """Inicia sesión con las credenciales proporcionadas."""
    try:
        wait = WebDriverWait(driver, 15)  # Aumentar el tiempo de espera a 30 segundos
        print("buscnaod botones")
        # Esperar a que los campos de usuario y contraseña estén presentes
        
        username_field = wait.until(
            EC.presence_of_element_located((By.NAME, "mail"))
        )
        password_field = wait.until(
            EC.presence_of_element_located((By.NAME, "p"))
        )
        print("botenes encontrados")
        # Ingresar credenciales
        username_field.send_keys(username)
        password_field.send_keys(password)

        # Hacer clic en el botón de inicio de sesión
        login_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[2]/div[2]/form/input[3]"))
        )
        login_button.click()

        print("Inicio de sesión exitoso.")
    except Exception as e:
        print(f"Error al iniciar sesión: {e}")
        raise
