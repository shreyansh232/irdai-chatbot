import os
import requests
from bs4 import BeautifulSoup


PAGE_URL = "https://irdai.gov.in/circulars?p_p_id=com_irdai_document_media_IRDAIDocumentMediaPortlet&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&_com_irdai_document_media_IRDAIDocumentMediaPortlet_filterToDate=12%2F11%2F2025&_com_irdai_document_media_IRDAIDocumentMediaPortlet_filterFromDate=01%2F01%2F2023&_com_irdai_document_media_IRDAIDocumentMediaPortlet_resetCur=false&_com_irdai_document_media_IRDAIDocumentMediaPortlet_delta=93"

# storing all pdfs in a directory
os.makedirs("irdai_pdfs", exist_ok=True)

# get html of the page
html = requests.get(PAGE_URL).text

# convert html into structured parse tree
soup = BeautifulSoup(html, "html.parser")


# extract all anchor tags
links = soup.find_all("a", href=True)

# get pdf links
pdf_links = [link["href"] for link in links if ".pdf" in link["href"].lower()]

# remove the duplicates
pdf_links = set(pdf_links)

print(f"""Found {len(pdf_links)} pdfs""")

# download the pdfs
for i, url in enumerate(pdf_links, start=1):
    filename = f"{i}.pdf"
    filepath = f"irdai_pdfs/{filename}"

    if not os.path.exists(filepath):
        print(f"Downloading {filename}")
        data = requests.get(url).content

        with open(filepath, "wb") as f:
            f.write(data)

    else:
        print(f"Already exists: {filename}")
