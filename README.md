# Price Comparator

This script is a price comparison tool that searches for a specified product on two e-commerce websites: Casas Bahia and Magazine Luiza. It uses Selenium to automate the web browsing and PySimpleGUI to provide a simple graphical user interface (GUI) for user interaction.

## Features 

- *Product Search*: Enter the name of the product you want to search for.
- *Price Comparison*: The script fetches the product prices from Casas Bahia and Magazine Luiza.
- *Lowest Price Display*: Displays the lowest price found along with the product link.
- *GUI*: Simple and intuitive GUI using PySimpleGUI.

## Requirements 

- Python 3.x
- Selenium
- PySimpleGUI

## Installation 

1. Clone the repository:
```bash
git clone https://github.com/yourusername/price-comparator.git
cd price-comparator
```

2. Install the required Python packages:
```bash
pip install -r requirements.txt
```

## Usage 

1. Run th script:
```bash
python app.py
```

2. Enter the product name:

- A GUI window will appear.
- Enter the name of the product you want to search for in the input field.
- Click the "Search" button.

3. View the results:

- The script will display the lowest price found and the corresponding product link in the GUI window.

### Code Overview

**Main Functions**

- start_driver(): Initializes the Selenium WebDriver with the specified options.
- search_product(driver, wait, product): Searches for the product on Casas Bahia and Magazine Luiza, and returns the sorted prices and links.
- compare_price(driver, wait, product, update_status): Compares the prices from both websites and updates the GUI with the lowest price and product link.
- handle_product_input(product): Validates the product input from the user.
- close_browser(driver): Closes the Selenium WebDriver.

**GUI**

- main(): Sets up the PySimpleGUI window and handles user interactions.

## License

This project is licensed under the MIT License. See the LICENSE file for details.