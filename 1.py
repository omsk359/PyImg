from bs4 import BeautifulSoup
import requests

import numpy as np
import cv2
import matplotlib.pyplot as plt

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 

from urllib.parse import urlparse
from io import BytesIO
from tld import get_tld
import re
import json


from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font

from pathlib import Path

import time
# import logging

# logging.basicConfig(filename="logfile.txt")
# stderrLogger=logging.StreamHandler()
# stderrLogger.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
# logging.getLogger().addHandler(stderrLogger)

import logging
import sys


root = logging.getLogger()
root.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

# create file handler which logs even debug messages
fh = logging.FileHandler('spam.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
root.addHandler(fh)




executable_path = {'executable_path':'/home/horo/bin/phantomjs', 'load_images': False}

def get_links_from_xlsx(file_name):
    wb = load_workbook(file_name)
    ws = wb.active
    rows = [row[0].value for row in ws.rows]
    # rows = []
    # for row in ws.rows:
        # l = [cell.value for cell in row]
        # rows.append(l)
    return rows


def parse_link(url):
	logging.info('Url: ' + url)
	parsed_url = urlparse(url)
	host = get_tld(url)

	global soup, br

	def get_soup():
		r = requests.get(url)
		soup = BeautifulSoup(r.text, 'html.parser')
		return soup
	
	def init_br():
		from splinter import Browser
		global br#nonlocal br
		if br == None:
			br = Browser('phantomjs', **executable_path)
		br.visit(url)
	br = None


	if host == 'amazon.com':
		# soup = get_soup()
		# img_el = soup.select('#landingImage')[0]
		# img_url = img_el['src']
		# price = soup.select('#priceblock_ourprice')[0].get_text()

		init_br()
		img_el = br.find_by_css('#landingImage')
		img_url = img_el['src']
		price_el = br.find_by_css('#priceblock_ourprice')
		price = price_el.html

	elif host == 'aliexpress.com':
		soup = get_soup()
		img_el = soup.select('#magnifier .ui-image-viewer-thumb-frame img')[0]
		img_url = img_el['src']
		price = soup.select('.p-current-price .p-price')[0].get_text()# + \
				#soup.select('.p-current-price .p-symbol')[0].get_text()
	elif host == 'alibaba.com':
		soup = get_soup()
		img_el = soup.select('#J-dcv-image-trigger')[0]
		img_url = img_el['src']
		price = soup.select('.ma-ref-price')[0].get_text()
	elif host == 'taobao.com':
		init_br()
		img_el = br.find_by_css('#J_ThumbView')
		img_url = img_el['src']
		price_el = br.find_by_css('.price-show .tb-rmb-num')
		# price = price_el.find_by_css('.tb-rmb').html + price_el.find_by_css('span').html
		price = re.sub(r'<.*?>', '', price_el.html)
		price = re.sub(r'\s+', '', price.replace('\n', ''))

		# img_el = soup.select('#J_ThumbView')[0]
		# img_url = img_el['src']
		# m = re.search('sibApi:"(.*)"', r.text)
		# url2 = 'https:' + m.group(1)
		# global g, r2
		# r2 = requests.get(url2, headers={'referer': url})
		# g = json.loads(r2.text)
		# try:
		# 	price = g['data']['promotionPrice']['skuPromotions']['def'][0]['price']
		# except:
		# 	price = soup.select('.price-show .tb-rmb-num')[0].get_text()
		# 	price = re.sub(r'\s+', ' ', price.replace('\n', ''))
	elif host == 'tmall.com':
		init_br()
		img_el = br.find_by_css('#J_ImgBooth')
		img_url = img_el['src']
		promo_el = br.find_by_css('.tm-promo-price')
		if promo_el.is_empty():
			promo_el = br.find_by_css('.tm-price-cur')
		price = promo_el.find_by_css('.tm-yen').html + promo_el.find_by_css('.tm-price').html
	elif host == 'ebay.com':
		soup = get_soup()
		img_el = soup.select('#icImg')[0]
		img_url = img_el['src']
		price_el = soup.select('#prcIsum')
		if len(price_el) == 0:
			price_el = soup.select('#mm-saleDscPrc')
		price = price_el[0].text
	elif host == 'iherb.com':
		soup = get_soup()
		img_el = soup.select('#iherb-product-image')[0]
		img_url = img_el['src']
		price_el = soup.select('#price')
		price = price_el[0].text.strip()
	elif host == 'jollychic.com':
		soup = get_soup()
		img_el = soup.select('.zoomer_img')[0]
		img_url = img_el['src']
		price_el = soup.select('#J-sku-price')
		price = price_el[0].text.strip()


	parsed_img_url = urlparse(img_url)
	if not parsed_img_url.scheme:
		img_url = parsed_img_url._replace(scheme=parsed_url.scheme).geturl()

	logging.info('Host: {}; Price: {}; Img: {}'.format(host, price, img_url))
	r_img = requests.get(img_url)
	img = Image.open(BytesIO(r_img.content))

	return img, price, host

def templateImgByDomain(domain):
	if domain == 'amazon.com':
		img = Image.open("templates/Amazon.png")
	elif domain == 'aliexpress.com':
		img = Image.open("templates/Aliexpress.png")
	elif domain == 'alibaba.com':
		img = Image.open("templates/Alibaba.png")
	elif domain == 'taobao.com':
		img = Image.open("templates/Taobao.png")
	elif domain == 'ebay.com':
		img = Image.open("templates/USA.png")
	elif domain == 'jollychic.com':
		img = Image.open("templates/Jollychic.png")
	elif domain == 'iherb.com':
		img = Image.open("templates/Iherb.png")
	elif domain == 'wyesstyle.com':
		img = Image.open("templates/Yesstyle.png")
	return img

def draw_img(img, text, type):
	templateImg = templateImgByDomain(type)
	new_img = img.resize(templateImg.size, Image.LANCZOS)
	new_img.paste(templateImg, None, templateImg)
	draw = ImageDraw.Draw(new_img)
	if type == 'amazon.com':
		font = ImageFont.truetype("FreeMono.ttf", 30, encoding="unic")
		draw.text((160, 15), text, (0,0,255), font=font)
	elif type == 'aliexpress.com':
		font = ImageFont.truetype("FreeMono.ttf", 30, encoding="unic")
		draw.text((870, 870), text, (0,0,255), font=font)
	elif type == 'alibaba.com':
		font = ImageFont.truetype("FreeMono.ttf", 30, encoding="unic")
		draw.text((150, 100), text, (0,0,255), font=font)
	elif type == 'taobao.com':
		font = ImageFont.truetype("FreeMono.ttf", 30, encoding="unic")
		draw.text((640, 60), text, (0,0,255), font=font)
	elif type == 'ebay.com':
		font = ImageFont.truetype("FreeMono.ttf", 30, encoding="unic")
		draw.text((680, 720), text, (255,255,255), font=font)
	elif type == 'jollychic.com':
		font = ImageFont.truetype("FreeMono.ttf", 30, encoding="unic")
		draw.text((780, 880), text, (0,0,255), font=font)
	elif type == 'iherb.com':
		font = ImageFont.truetype("FreeMono.ttf", 30, encoding="unic")
		draw.text((320, 100), text, (0,0,255), font=font)
	elif type == 'wyesstyle.com':
		font = ImageFont.truetype("FreeMono.ttf", 30, encoding="unic")
		draw.text((300, 0), text, (0,0,255), font=font)
	return new_img



in_file_name = 'in.xlsx'
delay = 1
out_dir = Path('./out')

links = get_links_from_xlsx(in_file_name)
logging.info('links', links)

if not out_dir.exists():
	out_dir.mkdir()


# links = [ 'https://www.alibaba.com/product-detail/video-call-infrared-vision-outdoor-security_60495998373.html?spm=a2700.7724856.main07.23.1a9823faXfrma&s=p' ]

# img = Image.open("test1.jpg")
# new_img = draw_img(img, 'eeer', 'alibaba.com')
# new_img.show()
# 1/0


err_i = []

for i, link in enumerate(links):
	# if not i == 14 and not i == 15:
	# 	continue
	try:
		img, price, domain = parse_link(link)
		new_img = draw_img(img, price, domain)
		file_name = str((out_dir / (str(i+1) + '.jpg')).absolute())
		logging.info('[{}/{}] Save to {}'.format(i+1, len(links), file_name))
		new_img.save(file_name)
		time.sleep(delay)
	except Exception as e:
		logging.exception(e)
		err_i.append(i)

logging.info('Ok/Fail: {}/{}'.format(len(links)-len(err_i), len(err_i)))
logging.info('Fail:')
for i in err_i:
	logging.error('{}: {}'.format(i+1, links[i]))


# price = '1.22'

# img = Image.open("416pfvtX78L._SY300_QL70_.jpg")
# draw = ImageDraw.Draw(img)
# # font = ImageFont.truetype(<font-file>, <font-size>)
# font = ImageFont.truetype("FreeMono.ttf", 15, encoding="unic")#ImageFont.load_default()
# # draw.text((x, y),"Sample Text",(r,g,b))
# draw.text((0, 0), price, (255,0,0), font=font)
# img.save('sample-out.jpg')
# img.show()

# r_img = requests.get(img_url)
# if r_img.status_code == 200:
#     with open("/home/horo/pyimg/1.jpg", 'wb') as f:
#         f.write(r_img.content)
# np.asarray(bytearray(r_img.content), dtype=np.uint8)
# image_array = np.asarray(bytearray(r_img.content), dtype=np.uint8)
# img = cv2.imdecode(image_array, -1)
# texted_image = cv2.putText(img=np.copy(img), text=price, org=(50,100),fontFace=3, fontScale=2, color=(0,0,255), thickness=2)

# plt.imshow(texted_image)
# plt.show()
