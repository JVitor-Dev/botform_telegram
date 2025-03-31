
import logging
import random
import asyncio
import datetime
import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.firefox import GeckoDriverManager
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configuração do logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurações
FORM_URL = "https://web.solvis.net.br/s/acpo"
IMPLICIT_WAIT = 10
PAGE_LOAD_TIMEOUT = 30
TELEGRAM_TOKEN = "7748196229:AAEkbcysbmzgIiWqJyVYhEylv59mudTumEw"

class FormElements:
    """Classe que contém os locators dos elementos do formulário"""
    def __init__(self):
        self.FORM_CONTAINER = (By.TAG_NAME, "form")
        self.EXPRESS_MOSSORO_LABEL = (By.XPATH, "//*[contains(text(), 'Express Mossoró')]")

def setup_webdriver():
    """Configura e retorna uma instância do Firefox WebDriver"""
    try:
        firefox_options = Options()
        firefox_options.add_argument('--headless')
        firefox_options.add_argument('--width=1920')
        firefox_options.add_argument('--height=1080')
        firefox_options.set_preference("browser.download.folderList", 2)
        firefox_options.set_preference("browser.download.manager.showWhenStarting", False)
        firefox_options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream")
        firefox_options.set_preference("browser.cache.disk.enable", False)
        firefox_options.set_preference("browser.cache.memory.enable", False)
        firefox_options.set_preference("browser.cache.offline.enable", False)
        firefox_options.set_preference("network.http.use-cache", False)

        logger.info("Configurando GeckoDriver...")
        service = Service(GeckoDriverManager().install())

        logger.info("Iniciando Firefox WebDriver...")
        driver = webdriver.Firefox(service=service, options=firefox_options)
        driver.implicitly_wait(3)

        logger.info("WebDriver iniciado com sucesso")
        return driver

    except Exception as e:
        logger.error(f"Erro ao configurar o WebDriver: {str(e)}")
        raise

class FormBot:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 5)
        self.form_url = FORM_URL
        self.elements = FormElements()

    def wait_for_element(self, locator):
        try:
            logger.debug(f"Aguardando elemento: {locator}")
            element = self.wait.until(EC.visibility_of_element_located(locator))
            logger.debug(f"Elemento encontrado: {locator}")
            return element
        except TimeoutException:
            logger.error(f"Timeout esperando pelo elemento: {locator}")
            raise
        except Exception as e:
            logger.error(f"Erro ao esperar elemento {locator}: {str(e)}")
            raise

    def wait_for_clickable(self, locator):
        try:
            logger.debug(f"Aguardando elemento clicável: {locator}")
            element = self.wait.until(EC.element_to_be_clickable(locator))
            logger.debug(f"Elemento clicável encontrado: {locator}")
            return element
        except TimeoutException:
            logger.error(f"Timeout esperando elemento ficar clicável: {locator}")
            raise
        except Exception as e:
            logger.error(f"Erro ao esperar elemento clicável {locator}: {str(e)}")
            raise

    def take_screenshot(self, name="screenshot"):
        try:
            if not os.path.exists("screenshots"):
                os.makedirs("screenshots")
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"screenshots/{name}_{timestamp}.png"
            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot salvo em: {filename}")
        except Exception as e:
            logger.error(f"Erro ao tirar screenshot: {str(e)}")

    def click_input_by_value(self, value):
        try:
            logger.debug(f"Procurando input com valor: {value}")
            self.wait.until(EC.presence_of_element_located((By.XPATH, f"//input[@value='{value}']")))
            input_element = self.driver.find_element(By.XPATH, f"//input[@value='{value}']")
            self.driver.execute_script("arguments[0].click();", input_element)
            logger.info(f"Input '{value}' clicado via JavaScript")
        except Exception as e:
            logger.error(f"Erro ao clicar no input '{value}': {str(e)}")
            raise

    def wait_and_log_page(self, page_name):
        try:
            logger.debug(f"Aguardando página {page_name} carregar")
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
            logger.debug(f"Página {page_name} carregada")
            self.take_screenshot(page_name)
        except Exception as e:
            logger.error(f"Erro ao aguardar página {page_name}: {str(e)}")
            raise

    def click_button_by_value(self, value):
        try:
            logger.debug(f"Procurando botão com valor: {value}")
            button = self.wait_for_clickable((By.XPATH, f"//input[@value='{value}']"))
            button.click()
            logger.info(f"Botão '{value}' clicado")
        except Exception as e:
            logger.error(f"Erro ao clicar no botão '{value}': {str(e)}")
            raise

    def fill_form(self):
        start_time = datetime.datetime.now()
        try:
            logger.info(f"Acessando URL: {self.form_url}")
            self.driver.get(self.form_url)
            logger.debug("Página inicial carregada")

            # Primeira página
            self.wait_and_log_page("pagina_inicial")
            express_mossoro = self.wait_for_clickable(self.elements.EXPRESS_MOSSORO_LABEL)
            express_mossoro.click()
            logger.info("Opção 'Express Mossoró' selecionada")
            self.take_screenshot("pagina_inicial_apos_selecao")
            self.click_button_by_value("Avançar")
            logger.info("ETAPA 1: Express Mossoró - Concluída")
            time.sleep(5)

            # Segunda página
            self.wait_and_log_page("segunda_pagina")
            opcao_escolhida = random.choice(['7', '8', '9'])
            self.click_input_by_value(opcao_escolhida)
            logger.info(f"Selecionada opção com valor: {opcao_escolhida}")
            self.take_screenshot("segunda_pagina_apos_selecao")
            self.click_button_by_value("Avançar")
            logger.info(f"ETAPA 2: Opção {opcao_escolhida} - Concluída")
            time.sleep(5)

            # Terceira página
            self.wait_and_log_page("terceira_pagina")
            opcoes_terceira_pagina = ['6616536', '6616537', '6616538', '6616539', '6616540', '6616541', '6616542', '6616543']
            selected_value = random.choice(opcoes_terceira_pagina)
            self.click_input_by_value(selected_value)
            self.take_screenshot("terceira_pagina_apos_selecao")
            self.click_button_by_value("Avançar")
            logger.info(f"ETAPA 3: Opção {selected_value} - Concluída")
            time.sleep(5)

            # Quarta página
            self.wait_and_log_page("quarta_pagina")
            self.click_input_by_value("6616544")
            self.click_input_by_value("6616547")
            self.take_screenshot("quarta_pagina_apos_selecao")
            self.click_button_by_value("Avançar")
            logger.info("ETAPA 4: Opções 6616544 e 6616547 - Concluída")
            time.sleep(5)

            # Quinta página
            self.wait_and_log_page("quinta_pagina")
            self.take_screenshot("quinta_pagina_antes_avancar")
            self.click_button_by_value("Avançar")
            logger.info("ETAPA 5: Avançar - Concluída")
            time.sleep(5)

            # Sexta página
            self.wait_and_log_page("sexta_pagina")
            self.click_input_by_value("6616553")
            self.take_screenshot("sexta_pagina_apos_selecao")
            self.click_button_by_value("Confirmar")
            logger.info("ETAPA 6: Opção 6616553 e Confirmar - Concluída")

            # Página final
            self.wait_and_log_page("pagina_final")
            execution_time = (datetime.datetime.now() - start_time).total_seconds()
            logger.info(f"Formulário preenchido com sucesso! Tempo de execução: {execution_time:.2f} segundos")
            return True

        except Exception as e:
            logger.error(f"Erro ao preencher formulário: {str(e)}")
            self.take_screenshot("erro_preenchimento")
            return False

def execute_bot():
    """Executa uma única instância do bot"""
    driver = None
    try:
        driver = setup_webdriver()
        bot = FormBot(driver)
        return bot.fill_form()
    except Exception as e:
        logger.error(f"Erro durante a execução do bot: {str(e)}")
        return False
    finally:
        if driver:
            try:
                driver.quit()
                logger.info("Navegador fechado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao fechar o navegador: {str(e)}")

# Comandos do Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Envia mensagem inicial"""
    logger.info("Comando /start recebido de %s", update.effective_user.id)
    await update.message.reply_text(
        "👋 Olá! Eu sou o bot de controle do preenchimento automático.\n\n"
        "Use o comando /executar <número> para iniciar o preenchimento automático.\n"
        "Exemplo: /executar 5 - para executar 5 vezes"
    )

async def executar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /executar <número> - Inicia o preenchimento automático"""
    try:
        logger.info("Comando /executar recebido de %s", update.effective_user.id)
        if not context.args:
            await update.message.reply_text("❌ Por favor, especifique o número de execuções.\nExemplo: /executar 5")
            return

        num_execucoes = int(context.args[0])

        if num_execucoes <= 0:
            await update.message.reply_text("❌ O número de execuções deve ser maior que zero.")
            return

        await update.message.reply_text(f"✅ Iniciando {num_execucoes} execuções...")

        sucessos = 0
        falhas = 0

        for i in range(num_execucoes):
            try:
                await update.message.reply_text(
                    f"🔄 Iniciando execução {i+1} de {num_execucoes}\n"
                    f"Status atual: ✅ {sucessos} sucessos, ❌ {falhas} falhas"
                )

                if execute_bot():
                    sucessos += 1
                    await update.message.reply_text(f"✅ Execução {i+1} concluída com sucesso!")
                    
                    if i < num_execucoes - 1:
                        intervalo_segundos = 300
                        await update.message.reply_text(f"⏱️ Aguardando {intervalo_segundos//60} minutos antes da próxima execução...")
                        await asyncio.sleep(intervalo_segundos)
                else:
                    falhas += 1
                    await update.message.reply_text(f"❌ Execução {i+1} falhou! Prosseguindo para a próxima execução sem aguardar.")

            except Exception as e:
                logger.error(f"Erro durante a execução {i+1}: {str(e)}")
                falhas += 1
                await update.message.reply_text(f"❌ Execução {i+1} falhou com erro: {str(e)}. Prosseguindo para a próxima execução sem aguardar.")
                continue

        await update.message.reply_text(
            f"📊 Relatório Final\n"
            f"Total de execuções: {num_execucoes}\n"
            f"✅ Sucessos: {sucessos}\n"
            f"❌ Falhas: {falhas}\n"
            f"Taxa de sucesso: {(sucessos/num_execucoes)*100:.1f}%"
        )

    except ValueError:
        await update.message.reply_text("❌ Por favor, forneça um número válido de execuções.")
        logger.error("Valor inválido fornecido para o comando /executar")
    except Exception as e:
        logger.error(f"Erro durante a execução: {str(e)}")
        await update.message.reply_text(f"❌ Ocorreu um erro durante a execução: {str(e)}")

def main():
    """Função principal do bot"""
    try:
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("executar", executar))
        logger.info("Iniciando bot do Telegram...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Erro ao iniciar o bot: {str(e)}")
        raise

if __name__ == "__main__":
    main()
