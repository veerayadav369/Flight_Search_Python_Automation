# Flight_Search_Python_Automation

# Flight Search Automation

This project automates the process of searching for flights between different cities using Selenium WebDriver. The script interacts with a travel website to find and display the top 5 cheapest flights for selected routes.

## Features
- Automatically logs in or dismisses login popups.
- Searches flights for specific routes and dates.
- Retrieves flight details such as price, duration, and airline.
- Outputs the results in a tabular format.
- Handles errors gracefully and retries failed actions.

## Technologies Used
- Python
- Selenium WebDriver
- WebDriver Manager
- Logging

## Installation

1. Clone the repository:
   ```bash
 [  git clone https://github.com/your-repo/flight-search-automation.git](https://github.com/veerayadav369/Flight_Search_Python_Automation.git)
   cd Flight_Search_Python_Automation
Create a virtual environment (optional but recommended):

bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install the required packages:

bash

pip install -r requirements.txt
Download the required browser driver automatically by WebDriver Manager.


Run the script:

bash

python designs.py
The results will be displayed in the terminal in a tabular format.

Known Issues
Flight details may show as Unknown if the website structure changes or if the script cannot locate the required elements.

Resetting the search form might fail occasionally, requiring a page reload.

Troubleshooting
Ensure the correct version of the Chrome browser and ChromeDriver are installed.

Make sure the website URL is correct and accessible.

Check the locators in the script to match the current structure of the website.

Contributing
Contributions are welcome! Please create an issue or submit a pull request with your changes.

License
This project is licensed under the MIT License. See the LICENSE file for details.

Acknowledgments
Selenium for browser automation.

WebDriver Manager for managing drivers.
