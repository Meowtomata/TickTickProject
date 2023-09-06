import requests
from datetime import date
from playwright.sync_api import sync_playwright

# automatically logins in as user in the background and retrieves the user token
# update to handle username and password error (as well as any others)
def get_token(username, password):
    print("Retrieving token...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto('https://ticktick.com/signin')
        page.fill('input#emailOrPhone', username)
        page.fill('input#password', password)
        page.locator('.button__3eXSs ').click()
        page.wait_for_selector('div#root.container-fill', state='visible')

        # Retrieve cookies from the current context and the URL you are interested in
        cookies = context.cookies("https://ticktick.com/webapp/")

        target_cookie_name = "t"
        target_cookie = next((cookie for cookie in cookies if cookie['name'] == target_cookie_name), None)

        if target_cookie:
            browser.close()
            cookie_value = target_cookie['value']
            return f"t={cookie_value}"
            
        else:
            print(f"Cookie with name '{target_cookie_name}' not found.")
            browser.close()

        return None     

# retrieve the user's TickTick data depending on the url
def get_data(url, token):
    # Necessary Headers to access data
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 OPR/99.0.0.0",
        "Cookie": f"{token}",
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return data

# StartDate and EndDate formats are YYYYMMDD
# timeline - Focus Record
# heatmap - trends, grids - useful for showing how much time I spent focusing on a particular day
# clockByDay - Timeline
# clock - Most Focused Time
# dist - Details - retrieves the Tasks, Tags, and Lists mapped to the amount of minutes spent on them within time interval
today = date.today().strftime("%Y%m%d")
def get_stats_from_to(token, type="dist", StartDate=today, EndDate=today):

    # TickTick's API URL to retrieve the tasks and the time spent on them from StartDate to EndDate
    url = f"https://api.ticktick.com/api/v2/pomodoros/statistics/{(type)}/{str(StartDate)}/{str(EndDate)}"
    # Return the data from the URL and format it into a more readable JSON format
    return get_data(url, token)

# handles the type of data user might want to retrieve
def get_url_data_type():
    
    input_data_type = input("""What type of data would you like to access today?\nType one of the following characters:
    t - timeline (your focus record)
    h - heatmap  (how much time you spent focusing on a particular day)
    c - clock    (the amount of focus time (in minutes) you've spent per each hour of the day)
    d - details  (retrieves the tasks, tags, and lists maps)\n""")
    
    match(input_data_type):
        case 't':
            return "dist/clockByDay"
        case 'h':
            return "heatmap"
        case 'c':
            return "dist/clock"
        case 'd':
            return "dist"
        case _:
            print("It seems like there was an error in your input. Try again!\n\n")
            return get_url_data_type()

# update later to better handle user errors
def parse_date():
    input_date = input("Enter your desired start date in YYYYMMDD format!")
    return input_date
    
def main(username, password, token):

    # prompts user for what type of data they want
    url_data_type = get_url_data_type()

    start_date = parse_date()    
    print(get_stats_from_to(token, url_data_type, start_date))
    
    # does the user want to retrieve more data?
    if get_more_data(): return main(username, password, token)

def get_more_data():

    get_more_input = input("Would you like more data? (Y/N)")
    match get_more_input:
        case 'Y': return 'Y'
        case 'N': return 'N'
        case _: return get_more_data()
    
if __name__ == '__main__':
    # retrieve the user's token given the user's username and password
    username = input("Input your username: ")
    password = input("Input your password: ")

    # using user input, retrieve the user's token
    token = get_token(username, password)

    main(username, password, token)
