from bs4 import BeautifulSoup
import requests

POST_URL = '''http://rbpdb.ccbr.utoronto.ca/cgi-bin/sequence_scan.pl'''

def predict(sequence):
    postParams = {'seq': sequence, 'thresh': 0.8}
    postOutput = requests.post(POST_URL, data=postParams)
    soup = BeautifulSoup(postOutput.text, features="lxml")
    table = soup.find('table', {'class', 'pme-main'})
    data = []

    if table:
        i = 0
        for row in table.findAll('tr'):
            if i == 0:
                headers_row = row.findAll('th')
                if headers_row:
                    headers = [header.string for header in headers_row][:6]
            else:
                data_row = row.findAll('td')
                if data_row:
                    data.append([cell.string for cell in data_row][:6])
            i += 1

    return headers, data

