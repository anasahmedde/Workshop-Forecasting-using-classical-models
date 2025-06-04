#Importing necessary libraries to work with
import sys
sys.path.append("..")
from modules.utils import datamining
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import pandas as pd
import time
from lxml import html
import joblib
import datetime
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--websiteLink', help='The link of the website. Default is semadata.org',type=str, default='https://apps.semadata.org/')
parser.add_argument('--username', help='Username credential for logging in. Default is NRehmtulla',type=str, default='')
parser.add_argument('--usernameXpath',help='Username field Xpath on the webpage. Default value is //input[@placeholder="Username"]' ,type=str, default="//input[@placeholder='Username']")
parser.add_argument('--password', help='Password credential for logging in. Default is Asc12345! ',type=str, default='')
parser.add_argument('--passwordXpath',help='Password field Xpath on the webpage. Default value is //input[@placeholder="Password"]' ,type=str, default="//input[@placeholder='Password']")
args = parser.parse_args()

# Username, password, link of website portal, xpath of username field and xpath of password field of the semadata.org portal
print('Website name: ',args.websiteLink)
print('Username Credential: ',args.username)
print('Username field Xpath: ',args.usernameXpath)
print('Password Credential: ',args.password)
print('Password field Xpath: ',args.passwordXpath)

websiteLink=args.websiteLink
username=args.username
usernameXpath=args.usernameXpath
password=args.password
passwordXpath=args.passwordXpath



#Importing necessary libraries to work with
import sys
sys.path.append("..")
from modules.utils import datamining
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import pandas as pd
import time
from lxml import html
import joblib
import datetime

datamining_methods=datamining()
driver=datamining_methods.start_browser(websiteLink,username,usernameXpath,password,passwordXpath)
# Checking whether python 2d List for brand name, brand id, product id, category of the product and part number of the 
# products is saved in the directory if not then it will initialized as an empty 2D list
try:
    all_data=joblib.load('all_brands_data.sav')
    brands_info=joblib.load('brands_info.sav')
except FileNotFoundError:
    all_data=[]
if len(all_data)!=0:
    print('Total no of products:',len(all_data))
else:
    print('No Previous data found! Now collecting the products data.')

#For collection of brand name, brand id, product id, category of the product and part number of the product
if len(all_data)==0:
    brands_info=[]
    for idx in range(1,len(Select(driver.find_element(By.ID,'receiver-brands')).options)):
        brand_id=driver.find_element(By.ID,'receiver-brands').find_elements(By.TAG_NAME,'option')[idx].get_attribute('value')
        Select(driver.find_element(By.ID,'receiver-brands')).select_by_index(idx)
        brand_name=driver.find_element(By.ID,'receiver-brands').find_elements(By.TAG_NAME,'option')[idx].text
        #An API to get the data of the products with their respective brand ID and product ID
        #temp_lst is the dictionary returned by the API call from browser console
        temp_lst=driver.execute_script('''
            var datas;
            await fetch("https://apps.semadata.org/Receiver/GetProducts", {
              "headers": {
                "accept": "application/json, text/javascript, */*; q=0.01",
                "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "x-requested-with": "XMLHttpRequest"
              },
              "referrer": "https://apps.semadata.org/",
              "referrerPolicy": "strict-origin-when-cross-origin",
              "body": "draw=2&columns%5B0%5D%5Bdata%5D=PartNumber&columns%5B0%5D%5Bname%5D=&columns%5B0%5D%5Bsearchable%5D=true&columns%5B0%5D%5Borderable%5D=true&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=CategoryName&columns%5B1%5D%5Bname%5D=&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=true&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=BrandName&columns%5B2%5D%5Bname%5D=&columns%5B2%5D%5Bsearchable%5D=true&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=AAIA_BrandID&columns%5B3%5D%5Bname%5D=&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=true&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B4%5D%5Bdata%5D=&columns%5B4%5D%5Bname%5D=&columns%5B4%5D%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=false&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&order%5B0%5D%5Bcolumn%5D=3&order%5B0%5D%5Bdir%5D=asc&start=0&length=1000000&search%5Bvalue%5D=&search%5Bregex%5D=false&brandID='''+brand_id+'''",
              "method": "POST",
              "mode": "cors",
              "credentials": "include"
            }).then((response) => response.json()).then((data)=>datas=data)
        return datas
        ''')
        brands_info.append([brand_name,len(temp_lst['data'])])
        print(f"{brand_name}: {len(temp_lst['data'])}")
        for instance in temp_lst['data']:
            all_data.append([instance['BrandName'],brand_id,str(instance['ProductID']),instance['CategoryName'],instance['PartNumber']])
    # After collecting the data, saving it in the local directory to save future time
    joblib.dump(brands_info, 'brands_info.sav')
    joblib.dump(all_data, 'all_brands_data.sav')
# Making CSV of the collected brands info about their respective quantity of products
df_brand=datamining_methods.makeCSV(brands_info,['Brand Name','Quantity of products'],'brands_info.csv')
# Initializing another webdriver as there will be 2 APIs call
helper_driver=datamining_methods.start_browser(websiteLink,username,usernameXpath,password,passwordXpath)
# Going to a base link of API to avoid Cross-Origin Resource Sharing (CORS) error
helper_driver.get('https://apps.semadata.org/Receiver/GetProductDetail')

# Checking whether python 2d List for detailed collected data of each product, products done counter and unreachable 
# products in directory is saved if not then it will initialized as an empty 2D list

try:
    excel_data=joblib.load('data_collected_so_far_2D_list.sav')
    unreachable=joblib.load('unreachable_products.sav')
    product_done=joblib.load('products_done_counter.sav')
except FileNotFoundError:
    excel_data=[]
    unreachable=[]
    product_done=0
print('Previously Collected Data: ',len(excel_data))
print('Unreachable Products: ',len(unreachable))
print('Products Scraped Successfully: ',product_done)

headersOfResultFile=['ProductID','Brand Name','Product URL','Vehicle Company','Vehicle Model','Quantity','Year','BrandID','Description','Part Number','Category','Price','Currency','Length','Width','Height','Weight','Weight UOM','Dimension UOM','Country Of Origin','Life Cycle Status Description','Refurbished Part','Package Level GTIN','Warranty Time','Warranty Time UOM','Taxable']
# This cell extracts the detailed information of the product and starts extracting data where left from.
try:
    for idx,instance in enumerate(all_data[product_done:]):
        print(f'{idx+product_done}- {instance[0]}')
        temporary_lst=[]
        description=None
        length=None
        width=None
        weight=None
        weight_UOM=None
        dimension_UOM=None
        height=None
        country_of_origin=None
        life_cycle_status_description=None
        refurbished_part=None
        package_level_GTIN=None
        warranty_time=None
        warranty_time_UOM=None
        taxable=None
        # An API to get detailed data of the product
        data=driver.execute_script('''
        var datas
        await fetch("https://apps.semadata.org/Receiver/GetProductDetail", {
          "headers": {
            "accept": "*/*",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-requested-with": "XMLHttpRequest"
          },
          "referrer": "https://apps.semadata.org/",
          "referrerPolicy": "strict-origin-when-cross-origin",
          "body": "productID='''+instance[2]+'''&brandID='''+instance[1]+'''",
          "method": "POST",
          "mode": "cors",
          "credentials": "include"
        }).then((response) => response.json()).then((data)=>datas=data)
        return datas
            ''')

        product_URL=f'https://apps.semadata.org/Receiver/GetProductPage?productID={instance[2]}'
        # receiving the raw HTML of the product and getting meaningful data from it
        html_text=helper_driver.execute_script('''
        var datas;
        await fetch("https://apps.semadata.org/Receiver/GetProductPage?productID='''+instance[2]+'''", {
          "headers": {
            "accept": "application/json",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1"
          },
          "referrer": "https://apps.semadata.org/",
          "referrerPolicy": "strict-origin-when-cross-origin",
          "body": null,
          "method": "GET",
          "mode": "cors",
          "credentials": "include"
        }).then((response) => response.text()).then((data)=>datas=data)
        return datas
        ''')
        try:
            # If raw HTML is recieved successfully then we will parsing it to HTML object
            html_API_call_method=True
            tree = html.fromstring(html_text)
        except ParserError:
            # If raw HTML is not recieved successfully then we will be going to the product page by browser
            html_API_call_method=False
            print('Trying with browser')
            helper_driver.get(f'https://apps.semadata.org/Receiver/GetProductPage?productID={instance[2]}')
            # Refreshing the browser due to unresponsiveness of the webpage
            try:
                helper_driver.refresh()
                element = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='product-detail-main']//span[contains(text(),'Part Type')]/parent::*/text()"))
                )
            except:
                # If unable to go the webpage then adding the info of that product to a list which can be dealt later
                unreachable.append(i)
                print('Unreachable: ',len(unreachable))
                continue
            driver.execute_script('''location.reload(true)''')
            driver.implicitly_wait(30)

        try:
            # If price is not in JSON data of the detailed product info then the product is to be skipped
            price=float(data['ProductAttributes'][5]['ProductAttributes'][0]['ProductAttributes'][len(data['ProductAttributes'][5]['ProductAttributes'][0]['ProductAttributes'])-1]['ValueText'])
        except TypeError:
            continue
        currency=data['ProductAttributes'][5]['ProductAttributes'][0]['ProductAttributes'][len(data['ProductAttributes'][5]['ProductAttributes'][0]['ProductAttributes'])-2]['ValueText']
        brand_name=instance[0]
        brand_id=instance[1]
        product_id=instance[2]
        category=instance[3]
        part_number=instance[4]
        if html_API_call_method:
            # If raw HTML is recieved successfully then we will parsing it to HTML object and getting data with Xpaths
            description=datamining_methods.assign(tree,"//div[@class='product-detail-main']//span[contains(text(),'Description')]/parent::*/text()")
            length=datamining_methods.assign(tree,"(//span[contains(text(),'Length')]/parent::*/text())[2]")
            width=datamining_methods.assign(tree,"(//span[contains(text(),'Width')]/parent::*/text())[2]")
            weight=datamining_methods.assign(tree,"(//span[contains(text(),'Weight')]/parent::*/text())[2]")
            weight_UOM=datamining_methods.assign(tree,"(//span[contains(text(),'Weight UOM')]/parent::*/text())[2]")
            dimension_UOM=datamining_methods.assign(tree,"(//span[contains(text(),'Dimension UOM')]/parent::*/text())[2]")
            height=datamining_methods.assign(tree,"(//span[contains(text(),'Height')]/parent::*/text())[2]")
            country_of_origin=datamining_methods.assign(tree,"(//span[contains(text(),'Country of Origin')]/parent::*/text())[2]")
            life_cycle_status_description=datamining_methods.assign(tree,"(//span[contains(text(),' Life Cycle Status Description')]/parent::*/text())[2]")
            refurbished_part=datamining_methods.assign(tree,"(//span[contains(text(),'Refurbished ')]/parent::*/text())[2]")
            package_level_GTIN=str(datamining_methods.assign(tree,"(//span[contains(text(),'Package Level GTIN')]/parent::*/text())[2]"))
            warranty_time=datamining_methods.assign(tree,"(//span[contains(text(),'Warranty Time')]/parent::*/text())[2]")
            warranty_time_UOM=datamining_methods.assign(tree,"(//span[contains(text(),'Warranty Time UOM')]/parent::*/text())[2]")
            taxable=datamining_methods.assign(tree,"(//span[contains(text(),'Taxable')]/parent::*/text())[2]")
        else:
            # If raw HTML is not recieved successfully then we will be going to the product page by browser and extract data
            description=helper_driver.execute_script('''
            try{return document.evaluate("//div[@class='product-detail-main']//span[contains(text(),'Description')]/parent::*/text()", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.textContent.trim()}
            catch{return ' '}
            ''')
            length=helper_driver.execute_script('''
            try{return parseFloat(document.evaluate("(//span[contains(text(),'Length')]/parent::*/text())[2]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.textContent.trim())}
            catch{return ' '}
            ''')
            width=helper_driver.execute_script('''
            try{return parseFloat(document.evaluate("(//span[contains(text(),'Width')]/parent::*/text())[2]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.textContent.trim())}
            catch{return ' '}
            ''')
            weight=helper_driver.execute_script('''
            try{return parseFloat(document.evaluate("(//span[contains(text(),'Weight')]/parent::*/text())[2]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.textContent.trim())}
            catch{return ' '}
            ''')
            weight_UOM=helper_driver.execute_script('''
            try{return document.evaluate("(//span[contains(text(),'Weight UOM')]/parent::*/text())[2]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.textContent.trim()}
            catch{return ' '}
            ''')
            dimension_UOM=helper_driver.execute_script('''
            try{return document.evaluate("(//span[contains(text(),'Dimension UOM')]/parent::*/text())[2]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.textContent.trim()}
            catch{return ' '}
            ''')
            height=helper_driver.execute_script('''
            try{return parseFloat(document.evaluate("(//span[contains(text(),'Height')]/parent::*/text())[2]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.textContent.trim())}
            catch{return ' '}
            ''')
            country_of_origin=helper_driver.execute_script('''
            try{return document.evaluate("(//span[contains(text(),'Country of Origin')]/parent::*/text())[2]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.textContent.trim()}
            catch{return ' '}
            ''')
            life_cycle_status_description=helper_driver.execute_script('''
            try{return document.evaluate("(//span[contains(text(),' Life Cycle Status Description')]/parent::*/text())[2]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.textContent.trim()}
            catch{return ' '}
            ''')
            refurbished_part=helper_driver.execute_script('''
            try{return document.evaluate("(//span[contains(text(),'Refurbished ')]/parent::*/text())[2]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.textContent.trim()}
            catch{return ' '}
            ''')
            package_level_GTIN=helper_driver.execute_script('''
            try{return document.evaluate("(//span[contains(text(),'Package Level GTIN')]/parent::*/text())[2]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.textContent.trim()}
            catch{return ' '}
            ''')
            warranty_time=helper_driver.execute_script('''
            try{return document.evaluate("(//span[contains(text(),'Warranty Time')]/parent::*/text())[2]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.textContent.trim()}
            catch{return ' '}
            ''')
            warranty_time_UOM=helper_driver.execute_script('''
            try{return document.evaluate("(//span[contains(text(),'Warranty Time UOM')]/parent::*/text())[2]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.textContent.trim()}
            catch{return ' '}
            ''')
            taxable=helper_driver.execute_script('''
            try{return document.evaluate("(//span[contains(text(),'Taxable')]/parent::*/text())[2]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.textContent.trim()}
            catch{return ' '}
            ''')
        # Checking whether detailed data of the product exists if not then skipping the product
        try:
            data['ProductConfig']
        except KeyError:
            continue
        # Storing list object of product detailled info with the time period of when the part number of vehicle was sold
        for detailed_data in data['ProductConfig']:
            vehicle_company=detailed_data['MakeName']
            vehicle_model=detailed_data['ModelName']
            quantity=detailed_data['Quantity']
            if detailed_data['YearID']==None:
                continue
            try:
                year=datetime.datetime.strptime(detailed_data['YearID'], "%Y").year
            except ValueError:
                year=detailed_data['YearID']
            # If year is not present then skipping that instance of product information
            if year==None:
                continue
            temporary_lst.append([product_id,brand_name,product_URL,vehicle_company,vehicle_model,quantity,year,brand_id,description,part_number,category,price,currency,length,width,height,weight,weight_UOM,dimension_UOM,country_of_origin,life_cycle_status_description,refurbished_part,package_level_GTIN,warranty_time,warranty_time_UOM,taxable])
        # Sorting the temporary list with year and then storing it to the main list that is excel_data
        temporary_lst.sort(key=lambda date_object: date_object[6])
        for temporary_instance in temporary_lst:
            excel_data.append(temporary_instance)
    # If detailed information of all the products have been collected successfully then it will save the collected data 
    # into the directory
    print('Extraction Completed!')
    joblib.dump(excel_data, 'data_collected_so_far_2D_list.sav')
    joblib.dump(unreachable, 'unreachable_products.sav')
    joblib.dump(idx+product_done,'products_done_counter.sav')
    df=datamining_methods.makeCSV(excel_data,headersOfResultFile,'final.csv')
except Exception as e:
    # If any error occurs it will save the current state of the extraction and print the error so that it can be debugged
    print(e)
    print(idx+product_done)
    joblib.dump(excel_data, 'data_collected_so_far_2D_list.sav')
    joblib.dump(unreachable, 'unreachable_products.sav')
    joblib.dump(idx+product_done,'products_done_counter.sav')
    df=datamining_methods.makeCSV(excel_data,headersOfResultFile,'final.csv')
