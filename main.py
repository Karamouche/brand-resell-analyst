from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import bs4
import time
import requests


def get_brands(brands_file):
	brands_list = brands_file.find_all('loc')
	brands_name = [loc.text for loc in brands_list]
	del brands_list[0]
	del brands_name[0]
	brands_name = [brand[28:] for brand in brands_name]
	brands_name = [brand.replace('-', ' ') for brand in brands_name]
	return {'link': brands_list, 'name': brands_name}


def fetch_items(brand_link):
	driver = webdriver.Firefox()
	driver.get(brand_link)
	try:
		time.sleep(2)
		driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
	except:
		pass

	links = []
	while len(links) < 2000:
		grid = driver.find_element(By.CLASS_NAME, "feed-grid")
		items = driver.find_elements(By.CLASS_NAME, "web_ui__ItemBox__image-container")
		links_page = [item.find_element(By.TAG_NAME, "a").get_attribute("href") for item in items]

		closet = driver.find_element(By.CLASS_NAME, "closet-container")
		closet = closet.find_elements(By.CLASS_NAME, "web_ui__ItemBox__image-container")
		closet_link = [item.find_element(By.TAG_NAME, "a").get_attribute("href") for item in closet]

		for element in links_page:
			if element in closet_link:
				links_page.remove(element)
		links += links_page
		print(len(links))
		driver.find_element(By.CLASS_NAME, "web_ui__Pagination__next").click()
		time.sleep(4)
	driver.close()
	return links
	

def main():
	# open brands.xml
	with open('brands.xml', 'r') as f:
		brands_file = bs4.BeautifulSoup(f.read(), 'xml')

	brands = get_brands(brands_file)

	brand_name = "Geox"
	brand_name = brand_name.lower()
	if brand_name not in brands['name']:
		print("Brand not found. Please retry.")
		return
	brand_link = brands['link'][brands['name'].index(brand_name)].text
	items = fetch_items(brand_link)


if __name__ == '__main__':
	main()