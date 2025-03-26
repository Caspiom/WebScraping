import controller
import os
import re
import shutil
from urllib.parse import urljoin, urlparse

# Constantes
BASE_URL = 'https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos'
DOWNLOAD_FOLDER = "downloads/anexos_pdf"
ZIP_NAME = "downloads/Anexos.zip"
PDF_PATTERN = re.compile(r'(?i)(?=.*anexo).*\.pdf$')  # Case insensitive match for "anexo" + .pdf


def main():
    """Função principal que orquestra o processo de scraping e download."""
    try:
        # Configura ambiente
        controller.setup_download_directory(DOWNLOAD_FOLDER)

        # Obtém conteúdo da página
        soup = controller.fetch_page_content(BASE_URL)
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
            if controller.download_pdf_file(pdf_url, filepath):
                downloaded_files.append(filepath)

        # Cria arquivo ZIP e limpa diretório
        if downloaded_files:
            controller.create_zip_archive(downloaded_files, ZIP_NAME)
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