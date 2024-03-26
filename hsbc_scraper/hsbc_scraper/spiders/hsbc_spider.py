import scrapy
from bs4 import BeautifulSoup
import re
import uuid
class HsbcSpiderSpider(scrapy.Spider):
    name = "hsbc_spider"
    # allowed_domains = ['https://www.hsbc.com.mx/contacto/directorio-de-sucursales/']
    start_urls = ['https://www.hsbc.com.mx/contacto/directorio-de-sucursales/']

    # https://www.hsbc.com.mx/contacto/directorio-de-sucursales/

    def start_requests(self):

        base_url='https://www.hsbc.com.mx/contacto/directorio-de-sucursales/'

        yield scrapy.Request(
            url=base_url,
            callback=self.parse
        )
    
    def parse_new(self,new_url):

        yield scrapy.Request(
            url=new_url,
            callback=self.parse_details
        )

    def parse(self, response):

        soup=BeautifulSoup(response.text,'lxml')

        cities=soup.find_all('li',class_='row')
        for city in cities:
            city_name=city.find('h2',class_='A-BBST28R-RW-ALL sm-12').text
            # print(city_name)
            banks=city.find_all('article',class_='container sm-12 md-6 lg-4')
            for bank in banks:
                new_url=bank.find('a',class_='A-LNKC22R-RW-ALL')['href']
                new_url=f'https://www.hsbc.com.mx{new_url}'
                
                yield response.follow(new_url,callback=self.parse_details,meta={'city_name':city_name})

        

    def parse_details(self,response):
            new_soup=BeautifulSoup(response.text,'lxml')
            name=new_soup.find('h2',class_='A-PAR22R-RW-ALL').text
            address=new_soup.find('p',class_='A-PAR16R-RW-ALL').text.replace('\n','').strip(' ')
            address=re.sub('\s+',' ',address)
            nums=re.findall('[0-9]+',address)
            nums=[int(num) for num in nums]
            post_code=max(nums)
            coord=new_soup.find('a',class_='A-BTNP-RW-ALL')['href'].split('destination=')[-1].split('/')
            lat=coord[0]
            lng=coord[1]
            phone=new_soup.find('div',class_='contact-container').find('p')
            if phone != None:
                phone=phone.text[11:].strip(' ')
            else:
                phone='Not available'
            working_hours=new_soup.find('ul',class_='A-LSTU-RW-ALL').find_all('li')
            for i in range(len(working_hours)):
                working_hours[i]=working_hours[i].text.replace('\n','').strip(' ')[-12:]
                if working_hours[i][-7:]=='Cerrado':
                    working_hours[i]='Closed'
            opening_hours=f'Mo: {working_hours[0]}; Tu: {working_hours[1]}; We: {working_hours[2]}; Th: {working_hours[3]}; Fr: {working_hours[4]}; Sa: {working_hours[5]} Su: {working_hours[6]}'
            
            data={  
                    'ref': uuid.uuid4().hex,  
                    'name': name,
                    'address': address,
                    'post_code': post_code,
                    'city_name': response.meta['city_name'],
                    'Country': 'Mexico',
                    'lat':lat,
                    'lng':lng,
                    'phone':phone,
                    'website': 'https://www.hsbc.com.mx/',
                    'store_url':response.url,
                    'Opening_hours':opening_hours,
            }
            yield (data)