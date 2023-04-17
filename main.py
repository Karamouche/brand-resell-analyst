from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import bs4
import time
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# constants
SAMPLE_SIZE = 200
BROWSER = "firefox"
ISMULTITHREAD = True
THREADS = 4

def setup_driver(headless=False):
	options = webdriver.FirefoxOptions() if BROWSER == "firefox" else webdriver.ChromeOptions()
	if headless:
		options.add_argument("--headless")
	options.add_argument("--no-sandbox")
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
	wait = WebDriverWait(driver, 10)
	wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
	try:
		wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))).click()
		time.sleep(2)
	except:
		pass

	links = []
	print("Fetching items links...")
	while len(links) < SAMPLE_SIZE: # get items links
		grid = driver.find_element(By.CLASS_NAME, "feed-grid")
		items = driver.find_elements(By.CLASS_NAME, "web_ui__ItemBox__image-container")
		links_page = [item.find_element(By.TAG_NAME, "a").get_attribute("href") for item in items]
		try:
			closet = driver.find_element(By.CLASS_NAME, "closet-container")
			closet = closet.find_elements(By.CLASS_NAME, "web_ui__ItemBox__image-container")
			closet_link = [item.find_element(By.TAG_NAME, "a").get_attribute("href") for item in closet]

			for element in links_page:
				if element in closet_link:
					links_page.remove(element)
		except:
			pass
		links += links_page
		if len(links) >= SAMPLE_SIZE:
			print("100%")
			break
		print("{:.2f}%".format(len(links)/SAMPLE_SIZE*100))
		wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "web_ui__Pagination__next"))).click()
		#driver.find_element(By.CSS_SELECTOR, "a.web_ui__Pagination__next").click()
	driver.close()
	return links


def get_items_info(items_link, driver):
	items = list()
	for link in items_link:
		wait = WebDriverWait(driver, 10)
		wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
		print(items_link.index(link)+1, "/", len(items_link))
		driver.get(link)
		item = {}
		try:
			item['name'] = driver.find_element(By.CLASS_NAME, "details-list--info").find_element(By.TAG_NAME, "h2").text
		except:
			pass

		item['link'] = link
		try:
			types = driver.find_element(By.XPATH, "/html/body/main/div/section/div/main/div/section[2]/div/div[1]/nav").find_elements(By.TAG_NAME, "a")
			item['category'] = types[len(types)-2].text
		except:
			pass
		
		try:
			item['price'] = driver.find_element(By.TAG_NAME, "h1").text.replace(' €', '').replace(',', '.')
			item['price'] = float(item['price'])
		except:
			pass

		item_details = driver.find_element(By.CLASS_NAME, "details-list--details").find_elements(By.CLASS_NAME, "details-list__item")
		for detail in item_details:
			if "TAILLE" in detail.text or "SIZE" in detail.text:
				size = detail.find_element(By.CLASS_NAME, "details-list__item-value").text
				size = size.split("\n")[0]
				item['size'] = size
			elif "ÉTAT" in detail.text or "CONDITION" in detail.text:
				condition = detail.find_element(By.CLASS_NAME, "details-list__item-value").text
				condition = condition.split("\n")[0]
				item['condition'] = condition
			elif "COULEUR" in detail.text or "COLOUR" in detail.text:
				color = detail.find_element(By.CLASS_NAME, "details-list__item-value").text
				color = color.split("\n")[0]
				item['color'] = color
			elif "NOMBRE DE VUES" in detail.text or "VIEWS" in detail.text:
				views = detail.find_element(By.CLASS_NAME, "details-list__item-value").text
				views = views.split(" ")[-1]
				views = int(views)
				item['views'] = views
			elif "INTÉRESSÉS·ÉES" in detail.text or "INTERESTED" in detail.text:
				interested = detail.find_element(By.CLASS_NAME, "details-list__item-value").text
				interested = interested.split(" ")[0]
				interested = int(interested)
				item['interested'] = interested
		items.append(item)
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
	del brands
	items = fetch_items(brand_link)
	print("Fetching items info...")
	
	if ISMULTITHREAD:
		chunks = [items[i::THREADS] for i in range(THREADS)]
		drivers = [setup_driver(True) for i in range(THREADS)]
		with ThreadPoolExecutor(max_workers=THREADS) as executor:
			futures = executor.map(get_items_info, chunks, drivers)
			result = list(futures)
		result = [item for sublist in result for item in sublist]
		[driver.close() for driver in drivers]
	else:
		driver = setup_driver(True)
		result = get_items_info(items, driver)
		driver.quit()
	df = pd.DataFrame(result)
	df.to_csv('{}_items.csv'.format(brand_name), index=False)
	print(df.head(5))
	


if __name__ == "__main__":
	main()