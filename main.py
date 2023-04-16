from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import bs4
import time
import requests
import pandas as pd

# constants
SAMPLE_SIZE = 400
BROWSER = "firefox"

def setup_driver(headless=False):
	options = webdriver.FirefoxOptions() if BROWSER == "firefox" else webdriver.ChromeOptions()
	if headless:
		options.add_argument("--headless")
	if BROWSER == "firefox":
		driver = webdriver.Firefox(options=options)
	elif BROWSER == "chrome":
		driver = webdriver.Chrome(options=options)
	else:
		print("Browser not supported. Please retry.")
		return
	return driver


def get_brands(brands_file):
	brands_list = brands_file.find_all('loc')
	brands_name = [loc.text for loc in brands_list]
	del brands_list[0]
	del brands_name[0]
	brands_name = [brand[28:] for brand in brands_name]
	brands_name = [brand.replace('-', ' ') for brand in brands_name]
	return {'link': brands_list, 'name': brands_name}


def fetch_items(brand_link):
	driver = setup_driver(True)
	driver.get(brand_link)
	try:
		time.sleep(2)
		driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
	except:
		pass

	links = []
	print("Fetching items links...")
	while len(links) < SAMPLE_SIZE: # get items links
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

		percent = len(links)/SAMPLE_SIZE*100
		if percent > 100:
			percent = 100
		print("{:.2f}%".format(percent))

		driver.find_element(By.CLASS_NAME, "web_ui__Pagination__next").click()
		time.sleep(4)
	driver.close()
	return links

def get_items_info(items_link):
	driver = setup_driver(True)
	items = list()
	print("Fetching items info...")
	for link in items_link:
		print("{:.2f}%".format(items_link.index(link)+1 / len(items_link) * 100))
		driver.get(link)
		try:
			time.sleep(2)
			driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
		except:
			pass
		time.sleep(2)
		item = {}
		try:
			print(driver.find_element(By.CLASS_NAME, "details-list--info").find_element(By.TAG_NAME, "h2").text)
			item['name'] = driver.find_element(By.CLASS_NAME, "details-list--info").find_element(By.TAG_NAME, "h2").text
		except:
			pass

		item['link'] = link
		try:
			types = driver.find_element(By.XPATH, "/html/body/main/div/section/div/main/div/section[2]/div/div[1]/nav").find_elements(By.TAG_NAME, "a")
			item['category'] = types[len(types)-2].text
			item['sub_category'] = types[len(types)-1].text

			item['price'] = driver.find_element(By.TAG_NAME, "h1").text.replace(' €', '').replace(',', '.')
			item['price'] = float(item['price'])

			item_details = driver.find_element(By.CLASS_NAME, "details-list--details").find_elements(By.CLASS_NAME, "details-list__item")

			size = item_details[1].find_element(By.CLASS_NAME, "details-list__item-value").text
			item['size'] = size.split("\n")[0]

			condition = item_details[2].find_element(By.CLASS_NAME, "details-list__item-value").text
			item['condition'] = condition.split("\n")[0]
			item['color'] = item_details[3].find_element(By.CLASS_NAME, "details-list__item-value").text
		except:
			pass

		items.append(item)

	driver.close()
	return items
	

def main():
	# open brands.xml
	with open('brands.xml', 'r') as f:
		brands_file = bs4.BeautifulSoup(f.read(), 'xml')

	brands = get_brands(brands_file)

	brand_name = str(input("Enter brand name: "))
	brand_name = brand_name.lower()
	if brand_name not in brands['name']:
		print("Brand not found. Please retry.")
		return
	brand_link = brands['link'][brands['name'].index(brand_name)].text
	items = fetch_items(brand_link)
	print("Fetching items info...")
	items_data = get_items_info(items[:100])
	
	df = pd.DataFrame(items_data)
	df.to_csv('{}_items.csv'.format(brand_name), index=False)
	print(df.head(5))
	


if __name__ == "__main__":
	main()