from bs4 import BeautifulSoup  # PT: Extrai o código HTML de uma página | EN: Parses HTML content
import requests  # PT: Faz requisições HTTP para obter a URL | EN: Makes HTTP requests to fetch URLs
import re  # PT: Expressões regulares para filtrar textos | EN: Regular expressions for pattern matching
import os  # PT: Operações com sistema de arquivos | EN: Filesystem operations
import zipfile  # PT: Cria arquivos ZIP | EN: Creates ZIP archives
from urllib.parse import urljoin, urlparse  # PT: Converte URLs relativas em absolutas | EN: Converts relative to absolute URLs
import shutil

url = 'https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos' # PT: URL alvo para scraping | EN: Target URL for scraping
download_folder = "anexos_pdf" # PT: Pasta para salvar PDFs | EN: Folder to save PDFs
zip_name = "Anexos.zip" # PT: Nome do arquivo ZIP de saída | EN: Output ZIP filename

# PT: Obtém o HTML da página | EN: Fetches page HTML
html_text = requests.get(url).text
soup = BeautifulSoup(html_text, 'html.parser')

# PT: Cria a pasta se não existir | EN: Creates folder if it doesn't exist
os.makedirs(download_folder, exist_ok=True)

# PT: Regex para "anexo" + .pdf | EN: Matches "anexo" + .pdf
pdf_pattern = re.compile(r'(?i)(?=.*anexo).*\.pdf$')
pdf_links = soup.find_all('a', href=pdf_pattern)

# PT: Lista para armazenar caminhos dos arquivos | EN: Stores downloaded file paths
downloaded_files = []

# Loop for procurando o regex | Loop for looking for the Regex
for link in pdf_links:
    # PT: Converte URL relativa para absoluta | EN: Converts relative to absolute URL
    full_url = urljoin(url, link['href'])

    # PT: Extrai o nome do arquivo da URL | EN: Extracts filename from URL
    parsed_url = urlparse(full_url)
    filename = os.path.basename(parsed_url.path)

    # PT: Caminho completo para salvar | EN: Full save path
    filepath = os.path.join(download_folder, filename)

    # PT: Log de download | EN: Download log
    print(f"Baixando: {filename}")
    pdf_response = requests.get(full_url)

    if pdf_response.status_code == 200:
        with open(filepath, "wb") as f:
            f.write(pdf_response.content)
        downloaded_files.append(filepath)
    else:
        print(f"Falha no download: {full_url}")

# PT: Cria arquivo ZIP | EN: Creates ZIP file
if downloaded_files:
    with zipfile.ZipFile(zip_name, "w") as zipf:
        for file in downloaded_files:
            zipf.write(file, os.path.basename(file))

    print(f"\nArquivos compactados com sucesso: {zip_name}")

    shutil.rmtree(download_folder)  # Remove a pasta | Remove folder

