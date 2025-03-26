import csv
from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Excel.Files import Files
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    open_robot_order_website()
    download_orders_csv()
    orders_table = read_csv_as_table()
    close_annoying_modal()
    loop_orders(orders_table)
    archive_receipts()

def open_robot_order_website():
    """Navigates to the given URL"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def download_orders_csv():
    """Downloads the orders CSV file from the given URL."""
    # Download the orders CSV file and overwrite if it already exists
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def read_csv_as_table():
    """Read data from csv and return as a table"""
    table = Tables().read_table_from_csv("orders.csv")
    return table

def loop_orders(orders_table):
    for order in orders_table:
        fill_the_form(order)

def fill_the_form(order):
    """Fills in the data"""
    page = browser.page()
    page.select_option("#head", order["Head"])
    body_value = order["Body"]
    page.click(f'input[name="body"][value="{body_value}"]')
    page.fill("input[placeholder='Enter the part number for the legs']", order["Legs"])
    page.fill("#address", order["Address"])
    while True:
        page.click("#order")
        order_another = page.query_selector("#order-another")
        if order_another:
            pdf_path = store_receipt_as_pdf(int(order["Order number"]))
            screenshot_path = screenshot_robot(int(order["Order number"]))
            order_another_bot()
            close_annoying_modal()
            break

def close_annoying_modal():
    """clicks the 'OK' button"""
    page = browser.page()
    page.click("button:text('OK')")

def order_another_bot():
    """Clicks on order another button to order another bot"""
    page = browser.page()
    page.click("#order-another")

def screenshot_robot(order_number):
    """Take a screenshot of the page"""
    page = browser.page()
    screenshot_path = "output/screenshots/{0}.png".format(order_number)
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    return screenshot_path

def embed_screenshot_to_receipt(screenshot_path, pdf_path):
    """Embeds the screenshot to the bot receipt"""
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(image_path=screenshot_path, 
                                   source_path=pdf_path, 
                                   output_path=pdf_path)

def store_receipt_as_pdf(order_number):
    """Export the data to a pdf file"""
    page = browser.page()
    order_receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_path = "output/receipts/{0}.pdf".format(order_number)
    pdf.html_to_pdf(order_receipt_html, pdf_path)
    return pdf_path

def archive_receipts():
    """Archives all the receipt pdfs into a single zip archive"""
    lib = Archive()
    lib.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")