class SimpleHttpTask(Task):
    url = None
    method = "GET"
    client: requests.Session = requests.Session()
print('done')
