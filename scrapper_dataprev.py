import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time

from dotenv import load_dotenv
load_dotenv()

url = os.getenv("DATAPREV_URL")

class DataprevScrapper:

    @staticmethod
    def extract_table_data(table):
        data = []

        thead = table.find('thead')
        if thead:
            header_row = thead.find('tr')
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
                data.append(headers)
        else:
            raise ValueError("Não foi possível obter os headers da tabela")

        tbody = table.find('tbody')
        rows = tbody.find_all('tr') if tbody else table.find_all('tr')[1:]

        if not rows:
            raise ValueError("Não foi possível obter as linhas da tabela")

        for row in rows:
            cells = row.find_all(['td', 'th'])
            row_data = [cell.get_text(strip=True) for cell in cells]
            if row_data:
                data.append(row_data)

        if not data or len(data[0]) == 0:
            raise ValueError("Não foi possível obter os dados da tabela")

        return data


    @staticmethod
    def scrappe_site():
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        try:
            print("🔧 Setting up Chrome driver...")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.get(url)
            time.sleep(10)

            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )
                print("✅ Page loaded successfully")
            except:
                return "⚠️ Tabela não encontrada no site da Dataprev."

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            table = soup.find('table', class_='views-table')

            if not table:
                return "A tabela de acompanhamentos não foi encontrado no site do Dataprev"

            data = DataprevScrapper.extract_table_data(table)

            if not data:
                driver.quit()
                return "Nenhum dado foi extraído da tabela"

            df = pd.DataFrame(data[1:], columns=data[0])
            df_filtrado = df[
                ["Classificação", "Candidato", "Inscrição", "Situação"]
            ]
            df_database = pd.read_csv("database.csv", dtype={"Classificação": str})

            # normalizar colunas
            for df_ in (df_filtrado, df_database):
                df_.columns = df_.columns.str.strip()
                df_["Inscrição"] = df_["Inscrição"].astype(str)


            df_diferenca = df_filtrado.merge(
                df_database,
                on="Inscrição",
                how="left",
                suffixes=("_novo", "_db")
            )

            df_diferenca = df_diferenca[
                (df_diferenca["Situação_novo"] != df_diferenca["Situação_db"]) |
                (df_diferenca["Situação_db"].isna())
            ]

            df_diferenca = df_diferenca[
                ["Classificação_novo", "Candidato_novo", "Inscrição", "Situação_novo"]
            ]
            df_diferenca.columns = ["Classificação", "Candidato", "Inscrição", "Situação"]

            if df_diferenca.empty:
                return None

            df_database.set_index("Inscrição", inplace=True)
            df_filtrado.set_index("Inscrição", inplace=True)
            df_database.update(df_filtrado)
            df_database.reset_index(inplace=True)
            df_database.to_csv("database.csv", index=False)

            driver.quit()
            alteracoes = df_diferenca[["Classificação", "Candidato", "Situação"]] \
                .to_dict(orient="records")

            return alteracoes


        except ValueError as err:
            return str(err)

        except Exception as err:
            return "Ocorreu um erro genérico ao rodar o scrapper"


