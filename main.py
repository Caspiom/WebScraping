import os
import re
import requests
import shutil
import zipfile
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# Constantes
BASE_URL = 'https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos'
DOWNLOAD_FOLDER = "anexos_pdf"
ZIP_NAME = "Anexos.zip"
PDF_PATTERN = re.compile(r'(?i)(?=.*anexo).*\.pdf$')  # Case insensitive match for "anexo" + .pdf
REQUEST_TIMEOUT = 10  # Timeout em segundos para requisições HTTP
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"


def setup_download_directory(directory_path: str) -> None:
    """Cria o diretório de download se ele não existir."""
    try:
        os.makedirs(directory_path, exist_ok=True)
    except OSError as error:
        print(f"Erro ao criar diretório {directory_path}: {error}")
        raise


def fetch_page_content(url: str) -> BeautifulSoup:
    """Obtém o conteúdo HTML da página."""
    headers = {'User-Agent': USER_AGENT}
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()  # Levanta exceção para status codes 4xx/5xx
        return BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as error:
        print(f"Erro ao acessar {url}: {error}")
        raise


def download_pdf_file(pdf_url: str, save_path: str) -> bool:
    """Faz download de um arquivo PDF e salva no caminho especificado."""
    headers = {'User-Agent': USER_AGENT}
    try:
        response = requests.get(pdf_url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        with open(save_path, 'wb') as file:
            file.write(response.content)
        return True
    except requests.RequestException as error:
        print(f"Falha no download de {pdf_url}: {error}")
        return False
    except IOError as error:
        print(f"Erro ao salvar arquivo {save_path}: {error}")
        return False


def create_zip_archive(file_paths: list, zip_filename: str) -> None:
    """Cria um arquivo ZIP contendo os arquivos especificados."""
    try:
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for file_path in file_paths:
                if os.path.exists(file_path):
                    zipf.write(file_path, os.path.basename(file_path))
                else:
                    print(f"Arquivo não encontrado: {file_path}")
        print(f"\nArquivos compactados com sucesso: {zip_filename}")
    except (zipfile.BadZipFile, IOError) as error:
        print(f"Erro ao criar arquivo ZIP {zip_filename}: {error}")
        raise


def main():
    """Função principal que orquestra o processo de scraping e download."""
    try:
        # Configura ambiente
        setup_download_directory(DOWNLOAD_FOLDER)

        # Obtém conteúdo da página
        soup = fetch_page_content(BASE_URL)
        pdf_links = soup.find_all('a', href=PDF_PATTERN)

        if not pdf_links:
            print("Nenhum link de PDF encontrado na página.")
            return

        # Processa downloads
        downloaded_files = []

        for link in pdf_links:
            pdf_url = urljoin(BASE_URL, link['href'])
            filename = os.path.basename(urlparse(pdf_url).path)
            filepath = os.path.join(DOWNLOAD_FOLDER, filename)

            print(f"Baixando: {filename}")
            if download_pdf_file(pdf_url, filepath):
                downloaded_files.append(filepath)

        # Cria arquivo ZIP e limpa diretório
        if downloaded_files:
            create_zip_archive(downloaded_files, ZIP_NAME)
            try:
                shutil.rmtree(DOWNLOAD_FOLDER)
            except OSError as error:
                print(f"Erro ao remover diretório {DOWNLOAD_FOLDER}: {error}")
        else:
            print("Nenhum arquivo foi baixado.")

    except Exception as error:
        print(f"Ocorreu um erro inesperado: {error}")


if __name__ == "__main__":
    main()