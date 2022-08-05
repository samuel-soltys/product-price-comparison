import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import unquote

# Some examples:
# product = "Huawei P30 Lite 4GB/128GB Dual SIM"
# product = "Samsung UE55TU7172"

product = input("Enter product to compare its prices: ")

productNajNakup = product.replace(" ", "-").replace("/", "-")

heurekaURL = f"https://www.heureka.sk/?h%5Bfraze%5D={product}"
najnakupURL = f"https://www.najnakup.sk/{productNajNakup}"

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"}

heureka = requests.get(heurekaURL, headers = headers)
najnakup = requests.get(najnakupURL, headers = headers)
print("requests.get finished")

soupHeureka = BeautifulSoup(heureka.content, 'html.parser')
soupNajNakup = BeautifulSoup(najnakup.content, 'html.parser')
print("soup finished")

buttonsHeureka = soupHeureka.findAll("a", {"class": "c-product__cta"})
buttonsNajNakup = soupNajNakup.findAll("a", {"class": "product-btn"})

productHeureka = requests.get(buttonsHeureka[0]['href'], headers = headers)

if str(buttonsNajNakup[0]['href']).find("jump") == -1:
    productNajNakup = requests.get("https://www.najnakup.sk" + buttonsNajNakup[0]['href'], headers = headers)
    soupNajNakup = BeautifulSoup(productNajNakup.content, 'html.parser')
    pricesNajNakup = soupNajNakup.findAll("strong", {"class": "total-rate"})
    eshopsNajNakup = soupNajNakup.findAll("a", {"class": "shoplogo_ponuka"})
else:
    soupNajNakup = BeautifulSoup(najnakup.content, 'html.parser')
    pricesNajNakup = soupNajNakup.findAll("strong", {"class": "total-rate"})
    eshopsNajNakup = soupNajNakup.findAll("a", {"class": "shoplogo_ponuka"})

soupHeureka = BeautifulSoup(productHeureka.content, 'html.parser')
pricesHeureka = soupHeureka.findAll("a", {"class": "pricen"})

lowestPrice = 999999
p = 0

for i in range(len(pricesHeureka)):
    pHeureka = float(pricesHeureka[i].get_text()[0:-2].replace(',', '.', 1).replace(' ','', 1)) # .strip(" "))
    if pHeureka < lowestPrice:
        heurekaResultURL = requests.get(pricesHeureka[i]['href'], headers = headers)
        if heurekaResultURL.status_code == 200:
            lowestPrice = pHeureka
            shopURL = heurekaResultURL.url

for i in range(len(pricesNajNakup)):
    start_index = 0
    end_index = 0
    pr = ""
    for s in range(len(pricesNajNakup[i].get_text())):
        if pricesNajNakup[i].get_text()[s] == '%':
            s = s + 2
            break 
        if (pricesNajNakup[i].get_text()[s].isdigit() or pricesNajNakup[i].get_text()[s] == '.'):
            pr = pr + pricesNajNakup[i].get_text()[s]
    pr = float(int(float(pr) * 100)) / 100
    pNajNakup = pr
    
    if pNajNakup < lowestPrice:
        najnakupResultURL = requests.get(eshopsNajNakup[i]['href'], headers = headers)
        if najnakupResultURL.status_code == 200:
            lowestPrice = pNajNakup
            for i in range(len(najnakupResultURL.url)):
                if i > 24:
                    if najnakupResultURL.url[i] == 'h' and najnakupResultURL.url[i + 1] == 't' and najnakupResultURL.url[i + 2] == 't' and najnakupResultURL.url[i + 3] == 'p':
                        start_index = i
                        shopURL = unquote(najnakupResultURL.url[start_index : len(najnakupResultURL.url)])
                        break

print(lowestPrice)
print(shopURL)