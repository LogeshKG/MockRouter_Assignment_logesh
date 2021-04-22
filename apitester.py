import requests
from tabulate import tabulate
from main import parser, ssh_cmd_executor

def generate_api(api_tag):
    if api_tag == "all":
        return "/all/interface/"
    return '/interface/' + str(api_tag)

def get_api_response(api):
        url = "http://localhost:5000" + api
        r = requests.get(url)
        return r.json()

def generate_table(response_list):
    total = []
    for response in response_list:
        headers = list(response.keys())
        total.append(list(response.values()))
    total.insert(0, headers)
    print(tabulate(total, headers="firstrow", tablefmt="grid"))

if __name__ == "__main__":
    def main(param):
        try:
            api = generate_api(param)
            response_list = get_api_response(api)
            generate_table(response_list)
        except Exception as err:
            print('Encountered an Exception: {}'.format(err))

    # with open('show_running-config.txt', 'r') as f:
    #     data = f.readlines()
    
    data = ssh_cmd_executor()
    data_parsed = parser(data)
    interfaces = [itr['interface_name'] for itr in data_parsed]
    interfaces.append('all')
    for param in interfaces:
        main(param)
        print('\n')