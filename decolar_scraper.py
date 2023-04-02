'''
    Neste arquivo é feita a navegação e consulta
    de preços de pacotes de viagem no site da
    Decolar
'''

from datetime import datetime
import time
from selenium_scraper import Scraper
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup

# Mapeamento dos elementos do site que serão utilizados
SITE_MAP = {
    'buttons': {
        'buscar': {  # Realiza a consulta
            'xpath': '//*[@id="searchbox-sbox-box-packages"]/div/div/div/div/div[3]/div[4]/button'
        },
        'cookie': {  # Fecha a barra de informação de cookie
            'xpath': '//*[@id="lgpd-banner"]/div/a[2]'
        },
        'aplicar_calendar': {  # Aplica a selecão de datas de partida e retorno
            'xpath': '//*[@id="component-modals"]/div[1]/div[2]/div[1]/button'
        }
    },
    'inputs': {
        'origem': {  # Campo de digitação da cidade de origem
            'xpath': '''//*[@id="searchbox-sbox-box-packages"]/div/div
                /div/div/div[3]/div[1]/div/div[1]/div[1]/div/input'''
        },
        'destino': {  # Campo de digitação da cidade de destino
            'xpath': '//*[@id="searchbox-sbox-box-packages"]/div/div/div/div/div[3]/div[1]/div/div[2]/div/div/input'
        },
        'dtini':{  # Campo da data de partida (não são digitáveis)
            'xpath_click': '//*[@id="searchbox-sbox-box-packages"]/div/div/div/div/div[3]/div[2]/div[1]/div[1]/div/div/div/div/input'
        },
        'dtfin':{  # Campo da data de retorno (não são digitáveis)
            'xpath_click': '//*[@id="searchbox-sbox-box-packages"]/div/div/div/div/div[3]/div[2]/div[1]/div[2]/div/div/div/div/input'
        },
        'calendar_container': {  # Calendário para escolha das datas de partida e retorno
            'xpath_month_year1': '//*[@id="component-modals"]/div[1]/div[1]/div[2]/div[1]',
            'xpath_month_year2': '//*[@id="component-modals"]/div[1]/div[1]/div[2]/div[2]',
            'xpath_button_left': '//*[@id="component-modals"]/div[1]/div[1]/div[2]/a[1]',
            'xpath_button_right': '//*[@id="component-modals"]/div[1]/div[1]/div[2]/a[2]',
        },
        'filtro_preco': { # filtro de ordenação de preço
            # Combo de seleção do filtro
            'xpath_filtro': '/html/body/aloha-app-root/aloha-results/div/div/div[2]/div[2]/div[2]/aloha-list-view-container/aloha-toolbar/div/aloha-order-inline/div/aloha-select/div/div/select',
            # Opção de preço do menor para o maior
            'xpath_option': '''/html/body/aloha-app-root/aloha-results/div/div/div[2]/div[2]/div[2]/
                aloha-list-view-container/aloha-toolbar/div/aloha-order-inline/div/aloha-select/div/div/select/option[1]'''
        }
    }
}


class Decolar(Scraper):
    '''
    Classe para webscraping usando selenium no site da decolar
    '''

    def __init__(self, navegador, url=''):
        super().__init__(navegador, url)

        # ActionChains usado para mover a página até o elemento para poder ser clicado
        self.actions = ActionChains(self.driver)

    # Verifica se o xpath já existe na página
    def _check_if_exists_xpath(self, xpath):
        try:
            self.driver.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            return False

        return True

    # Recupera o ano e o mês das colunas do calendário
    def _get_year_month(self):
        year1, month1 = [int(n) for n in self.driver.find_element(By.XPATH, SITE_MAP['inputs']['calendar_container']['xpath_month_year1']).get_attribute('data-month').split('-')]
        year2, month2 = [int(n) for n in self.driver.find_element(By.XPATH, SITE_MAP['inputs']['calendar_container']['xpath_month_year2']).get_attribute('data-month').split('-')]

        return year1, month1, year2, month2

    # Realiza a navegação pelo calendário para selecionar as datas corretas
    def _click_day_calendar(self, date):
        time.sleep(1)
        year1, month1, year2, month2 = self._get_year_month() # Recupera oo ano e o mês mostrados no calendário

        # Realiza a formatação das datas para processamento
        year_date = int(date.strftime('%Y'))
        month_date = int(date.strftime('%m'))
        day_date = int(date.strftime('%d'))

        # O calendário possui duas colunas de mês/ano
        # Enquanto nenhuma das colunas for igual ao mês e ano da data informada,
        # navega pelo calendário até achar o mês e ano correto.
        while ((year1 != year_date) and (year2 != year_date)) or ((month1 != month_date) and (month2 != month_date)):
            year1, month1, year2, month2 = self._get_year_month()

            # Caso o ano/mes no calendário forem menores que o ano/mes informado, clica na seta a direita
            if (year1 and year2 < year_date) or (month1 and month2 < month_date):
                self.driver.find_element(By.XPATH, SITE_MAP['inputs']['calendar_container']['xpath_button_right']).click()
            # Caso o ano/mes no calendário forem maiores que o ano/mes informado, clica na seta a esquerda
            elif (year1 and year2 > year_date) or (month1 and month2 > month_date):
                self.driver.find_element(By.XPATH, SITE_MAP['inputs']['month_date']['xpath_button_left']).click()

        # Pega a coluna correta com o mês informado
        if month1 == month_date:
            month_grid = self.driver.find_element(By.XPATH, SITE_MAP['inputs']['calendar_container']['xpath_month_year1']).find_element(By.CLASS_NAME, 'sbox5-monthgrid-dates')
        else:
            month_grid = self.driver.find_element(By.XPATH, SITE_MAP['inputs']['calendar_container']['xpath_month_year2']).find_element(By.CLASS_NAME, 'sbox5-monthgrid-dates')

        # Pega a lista de dias do mês
        days = month_grid.find_elements(By.CLASS_NAME, 'sbox5-monthgrid-datenumber')

        # Localiza o dia informado e clica no botão correspondente
        for day in days:
            if day.text[:2].isdigit():
                day_number = int(day.text[:2])
            else:
                day_number = int(day.text[0])

            if day_date == day_number:
                # Se o dia a ser clicado estiver como desabilitado, lança uma exceção
                if '-disabled' in day.get_attribute('class'):
                    raise Exception('Data indisponível. Impossível selecionar!')

                day.click()
                time.sleep(1)
                break


    def pesquisar_voo(self, origem, destino, dtini='', dtfin=''):
        '''
        Função para pesquisar os voos
        '''

        # Formata as datas para o tipo correto
        dtini = datetime.strptime(dtini, '%d/%m/%Y').date()
        dtfin = datetime.strptime(dtfin, '%d/%m/%Y').date()

        # Se existir uma faixa informativa sobre cookies, localiza o botão e fecha a faixa para evitar erros
        cookie_button = self.driver.find_element(By.XPATH, SITE_MAP['buttons']['cookie']['xpath'])
        if cookie_button:
            cookie_button.click()

        origem_element = self.driver.find_element(By.XPATH, SITE_MAP['inputs']['origem']['xpath']) # Localiza o elemento para digitação da cidade de origem
        self.actions.move_to_element(origem_element).perform() # Move a página até ele
        origem_element.click() # Clica no elemento (se não clicar, não aparece a lista de cidades ao digitar, e causa problemas ao consultar)
        origem_element.clear()
        time.sleep(1)
        origem_element.send_keys(origem) # Envia a cidade para o campo
        time.sleep(2)
        origem_element.send_keys(Keys.ENTER) # Envia um ENTER para selecionar a primeira cidade na lista

        # Realiza o mesmo processo do elemento acima
        destino_element = self.driver.find_element(By.XPATH, SITE_MAP['inputs']['destino']['xpath'])
        self.actions.move_to_element(destino_element).perform()
        destino_element.click()
        destino_element.clear()
        time.sleep(1)
        destino_element.send_keys(destino)
        time.sleep(2)
        destino_element.send_keys(Keys.ENTER)

        # Os campos de data não permitem digitação direta
        # Por isso é necessário clicar no campo, abrir o calendário e selecionar as datas por lá
        dtini_element = self.driver.find_element(By.XPATH, SITE_MAP['inputs']['dtini']['xpath_click'])
        self.actions.move_to_element(dtini_element).perform()
        dtini_element.click()

        self._click_day_calendar(dtini) # Seleciona no calendário a data de partida
        self._click_day_calendar(dtfin) # Seleciona no calendário a data de retorno

        calendar_aplicar_element = self.driver.find_element(By.XPATH, SITE_MAP['buttons']['aplicar_calendar']['xpath'])
        self.actions.move_to_element(calendar_aplicar_element).perform()
        calendar_aplicar_element.click() # Clica no botão aplicar no calendário

        buscar_element = self.driver.find_element(By.XPATH, SITE_MAP['buttons']['buscar']['xpath'])
        self.actions.move_to_element(buscar_element).perform()
        time.sleep(1)
        buscar_element.click() # Clica no botão buscar para realizar a consulta


    def get_menores_precos(self):
        '''
        Recupera os dados dos menores preços da primeira página (20 registros)
        '''

        # Aguarda o carregamento da página até que exista o combobox de filtro de preço
        while not self._check_if_exists_xpath(SITE_MAP['inputs']['filtro_preco']['xpath_option']):
            time.sleep(1)

        filtro_preco = self.driver.find_element(By.XPATH, SITE_MAP['inputs']['filtro_preco']['xpath_option'])

        filtro_preco.click()

        # Seleciona a opção de ordenação de preço do menor para o maior
        option_preco = self.driver.find_element(By.XPATH, SITE_MAP['inputs']['filtro_preco']['xpath_option'])
        option_preco.click()

        time.sleep(5)

        # Pega todo o código da página
        page_source = self.driver.page_source

        soup = BeautifulSoup(page_source, 'html.parser')

        # Pega todos os elementos de anuncios de pacotes
        scroll = soup.select_one('[infinitescroll]')

        anuncios = []

        if scroll:
            anuncios = scroll.find_all('div', {'class': 'results-cluster-container'})
        else:
            return

        for anuncio in anuncios:
            print(anuncio.find('span', {'class': 'accommodation-name'}).get_text())
            print(anuncio.find('aloha-location-name').find('span').get_text().replace('\n', '').strip())
            print(anuncio.find('span', {'class': 'main-value'}).get_text())

if __name__ == '__main__':
    try:
        decolar = Decolar('edge')

        decolar.abrir_site('https://www.decolar.com/pacotes/')
        decolar.pesquisar_voo('São Paulo', 'Tóquio', '06/11/2023', '22/11/2023')
        decolar.get_menores_precos()
    except Exception as err:
        print(f'Erro: {err}' )
        