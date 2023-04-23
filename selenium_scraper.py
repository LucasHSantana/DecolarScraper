'''
Arquivo com a classe principal Scraper utilizando selenium
'''

import os
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

BASE_DIR = os.path.dirname(os.path.abspath('__file__'))


class Scraper():
    '''
    Classe pai para webscraping usando selenium
    '''

    def __init__(self, navegador, url=''):
        self.navegador = navegador
        self.url = url

        # Configura o webdriver correto para o navegador
        if self.navegador == 'edge':
            # options = webdriver.EdgeOptions()
            # options.add_argument("--headless")

            # self._driver = webdriver.Edge(
            #   service=Service(EdgeChromiumDriverManager.install()),
            #   options=options
            # )
            self.driver = webdriver.Edge(
                service=Service(EdgeChromiumDriverManager().install())
            )
        else:
            print('navegador não implementado!')

    def abrir_site(self, url=''):
        '''
        Abre o navegador com a url informada
        '''

        if url:
            self.url = url

        if not self.url:
            raise ValueError('URL não informada!')

        # Maximiza a janela (Evita erros devido a mudança de layout no site)
        self.driver.maximize_window()
        self.driver.get(self.url)  # Abre o site
        self.driver.execute_script(
            'document.title = "Automação Busca Pacote Decolar"'
        )

    def close_browser(self):
        '''
        Fecha o driver
        '''
        self.driver.quit()

    def __del__(self):
        self.driver.quit()


if __name__ == '__main__':
    scraper = Scraper('edge', 'https://www.google.com')
    scraper.abrir_site()
