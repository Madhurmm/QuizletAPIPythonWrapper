import requests
import json
import time
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from pathlib2 import Path


class QuizletApiClass:
    WRITE_ACCESS_TOKEN, READ_ACCESS_TOKEN, READ_ACCESS_AUTHORIZATION_CODE, WRITE_ACCESS_AUTHORIZATION_CODE = ("",) * 4
    CLIENT_ID, SECRET_KEY, REDIRECT_URI, USERNAME, PASSWORD = ("",) * 5

    """ Fetch credentials, client id and  secret keys from json file """

    def read_creds(self):
        path = Path.cwd().joinpath('data').joinpath('private_creds.json')
        with open(path, 'r') as f:
            datastore = json.load(f)

            self.CLIENT_ID = datastore["CLIENT_ID"]
            self.SECRET_KEY = datastore["SECRET_KEY"]
            self.REDIRECT_URI = datastore["REDIRECT_URI"]
            self.USERNAME = datastore["USERNAME"]
            self.PASSWORD = datastore["PASSWORD"]

    """
    Get authorization code : https://quizlet.com/api/2.0/docs/authorization-code-flow
    
    Request parameter should include following mandatory terms :
    'response_type = code', 
    'client_id = {YOUR CLIENT ID}',
    'scope = write_set/read', 
    'state={ANY RANDOM STRING}'
    
    :param scope: should take one of two value : read/{or any string value}
    
    """

    def get_authorization_code(self, scope='read'):

        READ_AUTHORIZATION_CODE_URL = f'https://quizlet.com/authorize?response_type=code&client_id={self.CLIENT_ID}' \
                                      f'&scope=read&state=RANDOM_STRING'

        WRITE_AUTHORIZATION_CODE_URL = f'https://quizlet.com/authorize?response_type=code&client_id={self.CLIENT_ID}' \
                                       f'&scope=write_set&state=RANDOM_STRING'

        USERNAME_FIELD_SELECTOR = 'input[name=username]'
        PASSWORD_FIELD_SELECTOR = 'input[name=password]'
        LOGIN_BUTTON_SELECTOR = 'form > button'
        ALLOW_BUTTON_SELECTOR = 'button[name=allow]'

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(chrome_options=chrome_options)
        # driver = webdriver.Chrome()

        url = READ_AUTHORIZATION_CODE_URL if scope == 'read' else WRITE_AUTHORIZATION_CODE_URL

        driver.get(url)

        authorization_code = ''

        try:

            username_field = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, USERNAME_FIELD_SELECTOR)))
            username_field.send_keys(self.USERNAME)

            password_field = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, PASSWORD_FIELD_SELECTOR)))
            password_field.send_keys(self.PASSWORD)

            login_button = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, LOGIN_BUTTON_SELECTOR)))
            login_button.click()

            allow_button = WebDriverWait(driver, 30).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, ALLOW_BUTTON_SELECTOR)))
            allow_button.click()

            time.sleep(5)
            print(driver.current_url)
            authorization_code = driver.current_url.split('=')[-1]

        except Exception as e:
            print(e)

        finally:
            driver.quit()
            return authorization_code

    """ 
    Fetch read and write access token : https://quizlet.com/api/2.0/docs/authorization-code-flow
    :param scope: should take one of two value : read/{or any string value}
    
    """

    def get_access_token(self, scope):

        url = "https://api.quizlet.com/oauth/token"

        authorization_code = self.READ_ACCESS_AUTHORIZATION_CODE if scope == 'read' else self.WRITE_ACCESS_AUTHORIZATION_CODE
        clientid_secretkey_base64 = base64.b64encode(bytes(f'{self.CLIENT_ID}:{self.SECRET_KEY}', 'utf-8')).decode(
            "utf-8")

        payload = {
            'grant_type': 'authorization_code',
            'code': authorization_code
        }

        headers = {
            'redirect_uri': f"{self.REDIRECT_URI}",
            'authorization': f"Basic {clientid_secretkey_base64}",
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
        }

        response = requests.request("POST", url, data=payload, headers=headers)

        datastore = json.loads(response.text)
        return datastore['access_token']

    """ 
    Fetch the read/write access token from local json file (cache).
    
    If local json file is not present, it will create one from the scratch.
    
    File should contain two key-value pairs.
    2 keys should be viz. READ_ACCESS_TOKEN, WRITE_ACCESS_TOKEN
        
    """

    def fetch_read_write_access_token_from_cache(self):

        path = Path.cwd().joinpath('data').joinpath(f'access_token_cache_{self.CLIENT_ID}_{self.USERNAME}.json')

        if path.exists():
            with open(path, 'r') as f:
                datastore = json.load(f)
                self.READ_ACCESS_TOKEN = datastore["READ_ACCESS_TOKEN"]
                self.WRITE_ACCESS_TOKEN = datastore["WRITE_ACCESS_TOKEN"]
                return self

        self.READ_ACCESS_AUTHORIZATION_CODE = self.get_authorization_code('read')
        self.READ_ACCESS_TOKEN = self.get_access_token('read')

        self.WRITE_ACCESS_AUTHORIZATION_CODE = self.get_authorization_code('write')
        self.WRITE_ACCESS_TOKEN = self.get_access_token('write')

        access_token_dict = {
            'READ_ACCESS_TOKEN': self.READ_ACCESS_TOKEN,
            'WRITE_ACCESS_TOKEN': self.WRITE_ACCESS_TOKEN
        }
        path = Path.cwd().joinpath('data').joinpath(f'access_token_cache_{self.CLIENT_ID}_{self.USERNAME}.json')

        with open(path, 'w') as f:
            json.dump(access_token_dict, f)

    """
    <Make sure you have generated necessary access tokens (run fetch_read_write_access_token_from_cache() method)> 
    
    Adds a new set.
    You can create new sets by specifying at least two terms.
    
    Required parameters :  
    
    :param title: 
    :param lang_def: 
    :param lang_terms: 
    :param term_def_list: (List of tuple. tuple contains term, definition pair.)  
    
    """

    def create_new_set(self, title='title', lang_def='en', lang_terms='en',
                       term_def_list=[('term1', 'def1'), ('term2', 'def2')]):

        url = "https://api.quizlet.com/2.0/sets"

        payload = [
            ('title', title),
            ('lang_definitions', lang_def),
            ('lang_terms', lang_terms),
        ]

        for tuple_sample in term_def_list:
            term, definition = tuple_sample
            payload.append(('terms[]', term))
            payload.append(('definitions[]', definition))

        headers = {
            'authorization': f"Bearer {self.WRITE_ACCESS_TOKEN}",
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
        }

        response = requests.request("POST", url, data=tuple(payload), headers=headers)

        return response.text

    """
    <Make sure you have generated necessary access tokens (run fetch_read_write_access_token_from_cache() method)> 
    
    Returns just the terms from set 
    :param set_id:
     
    """

    def fetch_terms_from_a_set(self, set_id='415'):

        url = f"https://api.quizlet.com/2.0/sets/{set_id}/terms"

        headers = {
            'authorization': f"Bearer {self.READ_ACCESS_TOKEN}",
            'cache-control': "no-cache",
        }

        response = requests.request("GET", url, headers=headers)

        return response.text

    """
    <Make sure you have generated necessary access tokens (run fetch_read_write_access_token_from_cache() method)> 
    
    Returns the set details, including all the terms.
    :param set_id: 
    
    """

    def fetch_all_details_from_a_set(self, set_id='415'):
        url = f"https://api.quizlet.com/2.0/sets/{set_id}"

        headers = {
            'authorization': f"Bearer {self.READ_ACCESS_TOKEN}",
            'cache-control': "no-cache",
        }

        response = requests.request("GET", url, headers=headers)

        return response.text

    """
    <Make sure you have generated necessary access tokens (run fetch_read_write_access_token_from_cache() method)>
    Adds a single term and definition in a set
    
    :param set_id: 
    :param term: 
    :param definition: 
    
    """

    def add_single_term(self, set_id, term='term', definition='definition'):
        url = f"https://api.quizlet.com/2.0/sets/{set_id}/terms"

        payload = (
            ('term', term),
            ('definition', definition)
        )

        headers = {
            'authorization': f"Bearer {self.WRITE_ACCESS_TOKEN}",
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
        }

        response = requests.request("POST", url, data=payload, headers=headers)

        return response.text

    """
    <Make sure you have generated necessary access tokens (run fetch_read_write_access_token_from_cache() method)>
    
    Edits a single term mentioned by the term_id parameter    
    :param set_id: 
    :param term_id: 
    :param term: 
    :param definition:
     
    """

    def edit_single_term(self, set_id, term_id, term='new_term', definition='new_definition'):
        url = f"https://api.quizlet.com/2.0/sets/{set_id}/terms/{term_id}"

        payload = (
            ('term', term),
            ('definition', definition)
        )

        headers = {
            'authorization': f"Bearer {self.WRITE_ACCESS_TOKEN}",
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
        }

        response = requests.request("PUT", url, data=payload, headers=headers)

        return response.text

    """
    <Make sure you have generated necessary access tokens (run fetch_read_write_access_token_from_cache() method)>
    
    Deletes a single term from the set 
    :param set_id: 
    :param term_id: 
    
    """

    def delete_single_term(self, set_id, term_id):
        url = f"https://api.quizlet.com/2.0/sets/{set_id}/terms/{term_id}"

        headers = {
            'authorization': f"Bearer {self.WRITE_ACCESS_TOKEN}",
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
        }

        response = requests.request("DELETE", url, headers=headers)

        return response.text

    """
    <Make sure you have generated necessary access tokens (run fetch_read_write_access_token_from_cache() method)>
    
    When you add a terms (and optionally definition and/or image) array using this endpoint,
    you will replace all the terms in the set with what you posted. 
    Furthermore, if you want to change terms or definitions, you must submit at least all three of term_ids[], terms[] 
    and definitions[] and they MUST be the same size and in the same order.
    
    :param set_id:
    :param title:
    :param term_def_list: List of new pair of term and definition
    :return:

    """

    def edit_whole_set(self, set_id, title='title', term_def_list=[('term1', 'def1'), ('term2', 'def2')]):
        url = f"https://api.quizlet.com/2.0/sets/{set_id}"

        payload = [('title', title)]

        for tuple_sample in term_def_list:
            term, definition = tuple_sample
            payload.append(('terms[]', term))
            payload.append(('definitions[]', definition))

        headers = {
            'authorization': f"Bearer {self.WRITE_ACCESS_TOKEN}",
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
        }

        response = requests.request("PUT", url, data=tuple(payload), headers=headers)

        return response.text

    """"
    <Make sure you have generated necessary access tokens (run fetch_read_write_access_token_from_cache() method)> 
    
    Returns all the user's details, and minimal information of all their sets, classes, favorites 
    :param username:
        
    """

    def fetch_minimal_user_details(self, username='greatvocab_master'):
        url = f"https://api.quizlet.com/2.0/users/{username}"

        headers = {
            'authorization': f"Bearer {self.READ_ACCESS_TOKEN}",
            'cache-control': "no-cache",
        }

        response = requests.request("GET", url, headers=headers)

        return response.text

    """
    <Make sure you have generated necessary access tokens (run fetch_read_write_access_token_from_cache() method)>
    
    Deletes a set with particular set_id
    :param set_id: 
    :return:
     
    """

    def delete_set(self, set_id):
        url = f"https://api.quizlet.com/2.0/sets/{set_id}"

        headers = {
            'authorization': f"Bearer {self.WRITE_ACCESS_TOKEN}",
            'cache-control': "no-cache",
        }

        response = requests.request("DELETE", url, headers=headers)

        return response.text

