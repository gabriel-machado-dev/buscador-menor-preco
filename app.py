import PySimpleGUI as sg
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import logging as lg
import threading

DOWNLOAD_DIRECTORY = r'./lowerprice'

def start_driver():
    try:
        chrome_options = Options()

        arguments = [
            '--lang=pt-BR', '--window-size=1300,1000', '--disable-notifications', '--incognito', 
            '--block-new-web-contents', '--no-default-browser-check', 'window-position=36,68', 
            '--headless', 'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
        ]

        for argument in arguments:
            chrome_options.add_argument(argument)

        # Disable pop-up of browser controlled by automation
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])

        # Using experimental settings
        chrome_options.add_experimental_option('prefs', {
            # Change the default download location
            'download.default_directory': DOWNLOAD_DIRECTORY,
            # Notify Google Chrome about this change
            'download.directory_upgrade': True,
            # Disable download confirmation
            'download.prompt_for_download': False,
            # Disable notifications
            'profile.default_content_setting_values.notifications': 2,
            # Allow multiple downloads
            'profile.default_content_setting_values.automatic_downloads': 1,
        })

        driver = webdriver.Chrome(options=chrome_options)

        wait = WebDriverWait(
            driver,
            20,
            poll_frequency=1,
            ignored_exceptions=[
                NoSuchElementException,
                ElementNotVisibleException,
                ElementNotSelectableException,
                TimeoutException
            ]
        )

        return driver, wait
    except Exception as e:
        lg.error(f'Error occurred while initializing driver: {type(e).__name__} - {e}')
        return None, None

def search_product(driver, wait, product):
    try:
        driver.get(f'https://www.casasbahia.com.br/{product}/b')

        try:
            xpath_product_price_casas_bahia = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="product-card__highlight-price"]')))
            xpath_product_link_casas_bahia = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//a[@data-testid="product-card-link-overlay"]')))
            xpath_product_name_casas_bahia = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//h3[@class="product-card__title"]')))
        except TimeoutException:
            lg.error('Timeout while waiting for elements on Casas Bahia.')
            return [], []
        except Exception as e:
            lg.error(f'Error occurred while fetching product on Casas Bahia: {type(e).__name__} - {e}')
            return [], []

        data_casas_bahia = []

        for product_link, product_price, product_name in zip(xpath_product_link_casas_bahia, xpath_product_price_casas_bahia, xpath_product_name_casas_bahia):
            if len(product_price.text.replace('R$', '').replace(',', '').strip()) <= 5:
                product_price = float(product_price.text.replace('R$', '').replace(',', '.').strip())
            else:
                product_price = float(product_price.text.replace('R$', '').replace(',', '').strip())
            product_link = product_link.get_attribute("href")
            data_casas_bahia.append([product_price, product_link])

        sorted_values_casas_bahia = sorted(data_casas_bahia, key=lambda x: x[0])

        driver.get(f'https://www.magazineluiza.com.br/busca/{product}/')

        try:
            xpath_product_link_magalu = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//li[@class="sc-frWhYi mRyXo"]/a')))
            xpath_product_price_magalu = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="sc-dhKdcB ryZxx"]/p')))
            xpath_product_name_magalu = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//li[@class="sc-frWhYi mRyXo"]//div/h2')))
        except TimeoutException:
            lg.error('Timeout while waiting for elements on Magazine Luiza.')
            return sorted_values_casas_bahia, []
        except Exception as e:
            lg.error(f'Error occurred while fetching product on Magazine Luiza: {type(e).__name__} - {e}')
            return sorted_values_casas_bahia, []

        data_magalu = []

        for links, price, product_name in zip(xpath_product_link_magalu, xpath_product_price_magalu, xpath_product_name_magalu):
            link = links.get_attribute("href")
            product_price_magalu = float(price.text.split()[1].replace(',', ''))
            data_magalu.append([product_price_magalu, link])

        sorted_values_magalu = sorted(data_magalu, key=lambda x: x[0])

        return sorted_values_casas_bahia, sorted_values_magalu
    
    except Exception as e:
        lg.error(f'Error occurred while searching for product: {type(e).__name__} - {e}')
        return [], []

def compare_price(driver, wait, product, update_status):
    sorted_values_casas_bahia, sorted_values_magalu = search_product(driver, wait, product)

    try:
        if not sorted_values_casas_bahia and not sorted_values_magalu:
            update_status('No product found.')
            return

        lowest_price_casas_bahia = sorted_values_casas_bahia[0][0] if sorted_values_casas_bahia else float('inf')
        lowest_price_link_casas_bahia = sorted_values_casas_bahia[0][1] if sorted_values_casas_bahia else ''

        lowest_price_magalu = sorted_values_magalu[0][0] if sorted_values_magalu else float('inf')
        lowest_price_link_magalu = sorted_values_magalu[0][1] if sorted_values_magalu else ''

        if lowest_price_casas_bahia < lowest_price_magalu:
            update_status(f'Lowest price found: R${lowest_price_casas_bahia}')
            update_status(f'Product link: {lowest_price_link_casas_bahia}')
        else:
            update_status(f'Lowest price found: R${lowest_price_magalu}')
            update_status(f'Product link: {lowest_price_link_magalu}')

    except Exception as e:
        lg.error(f'Error occurred while comparing prices: {type(e).__name__} - {e}')
        update_status(f'Error occurred while comparing prices: {type(e).__name__} - {e}')
        return None
    
def handle_product_input(product):
    while True:
        if not product or product.isspace() or len(product) < 3:
            print('Enter a valid product.')
            product = input('Enter the product you want to search for: ')
        else:
            break
    return product

def close_browser(driver):
    try:
        driver.quit()
    except Exception as e:
        lg.error(f'Error occurred while closing the browser: {type(e).__name__} - {e}')
        return None 

def search_thread(product, window):
    driver, wait = start_driver()

    def update_status(message):
        window.write_event_value('-UPDATE-', message)

    try:
        compare_price(driver, wait, product, update_status)
    except Exception as e:
        lg.error(f'Error occurred while comparing prices: {type(e).__name__} - {e}')
        update_status(f'Error occurred while comparing prices: {type(e).__name__} - {e}')
    finally:
        close_browser(driver)
        window.write_event_value('-SEARCH_DONE-', '')

def main():
    sg.theme('SystemDefault')

    layout = [
        [sg.Text('Enter the product you want to search for:')],
        [sg.Input(key='-PRODUCT-', size=(35, 1))],
        [sg.Button('Search'), sg.Button('Exit')],
        [sg.Multiline(size=(40, 20), key='-OUTPUT-', autoscroll=True, disabled=True)]
    ]

    window = sg.Window('Price Comparator', layout)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Exit':
            break

        if event == 'Search':
            product = values['-PRODUCT-']
            product = handle_product_input(product)
            window['-OUTPUT-'].update('')
            window['Search'].update(disabled=True)
            window['Exit'].update(disabled=True)
            threading.Thread(target=search_thread, args=(product, window), daemon=True).start()

        if event == '-UPDATE-':
            window['-OUTPUT-'].update(values[event] + '\n', append=True)

        if event == '-SEARCH_DONE-':
            window['Search'].update(disabled=False)
            window['Exit'].update(disabled=False)

    window.close()

if __name__ == '__main__':
    main()