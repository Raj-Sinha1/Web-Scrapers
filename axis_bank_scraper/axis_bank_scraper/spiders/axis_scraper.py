import scrapy
from bs4 import BeautifulSoup


class AxisScraperSpider(scrapy.Spider):
    name = "axis_scraper"
    allowed_domains = ["branch.axisbank.com"]
    start_urls = ["https://branch.axisbank.com/"]
    
    
    def start_requests(self):

        base_url='https://branch.axisbank.com/'

        yield scrapy.Request(
            url=base_url,
            callback=self.parse
        )
    

    def get_state(self,response):
        soup=BeautifulSoup(response.text,'lxml')
        states=soup.find("select",id="customState")
        state_list=states.find_all('option')
        states=[state_name.get('value') for state_name in state_list[1:]]
        
        return states


    def parse(self, response):

        base_url='https://branch.axisbank.com'

        states=self.get_state(response=response)

        for state in states:
            i=1
            new_url=base_url+f'/location/{state}?page={i}'
            yield scrapy.Request(
                url=new_url,
                callback=self.parse_store
            )


    def parse_store(self,response):

        soup=BeautifulSoup(response.text,'lxml')

        stores=soup.find_all('li',class_='left-float store-info-box')
            
        for store in stores:
            ref=store.find('a',class_='phone-website height-manage')['onclick'][45:].split("'")[0]
            name=store.find('b').text
            if 'ATM' in name.split(' '):
                operating_hours="Mo: 12:00-11:59; Tu: 12:00-11:59; We: 12:00-11:59; Th: 12:00-11:59; Fr: 12:00-11:59; Sa: 12:00-11:59; Su: 12:00-11:59"
                # print(operating_hours)
            else:
                operating_hours="Mo: 09:30-15:30; Tu: 09:30-15:30; We: 09:30-15:30; Th: 09:30-15:30; Fr: 09:30-15:30; Sa: 09:30-15:30: Su: closed"
                # print(operating_hours)
            state=store.find_all('span',class_='address_axis')[0].text
            city=store.find_all('span',class_='address_axis')[1].text
            addr_full=store.find_all('span',class_='address_axis')[2].text
            address=soup.find_all('li',class_='left-float store-info-box')
            for item in address:
                number_of_attributes=len(item.find_all('span',class_='address_axis'))
                if number_of_attributes<7:
                    # operating_hours=item.find_all('span',class_='address_axis')[3].text
                    postcode=item.find_all('span',class_='address_axis')[4].text
                else:
                    # operating_hours=item.find_all('span',class_='address_axis')[4].text
                    postcode=item.find_all('span',class_='address_axis')[5].text        
            store_url=store.find('a',class_='store-name-color')['href']
            phone=store.find('a',class_='for-ph-desktop').text

            data={
                
                "ref":ref,
                "name":name,
                "addr_full":addr_full+" "+city+" "+state+" "+postcode,
                "city":city,
                "state":state,
                "country":"India",
                "phone":phone,
                "website":'https://branch.axisbank.com/',
                "store_url":store_url,
                "postcode":postcode,
                "operating hours":operating_hours,
                "lat":store.find('input',class_='outlet-latitude')['value'],
                "lon":store.find('input',class_='outlet-longitude')['value'],
            }

            yield (data)

            # https://branch.axisbank.com/location/nagaland?page=1

            next_button=soup.find('span',class_='next')
            if next_button is not None:
                next_page=next_button.find('a')['href']
                next_url="https://branch.axisbank.com"+next_page
                yield scrapy.Request(
                    url=next_url,
                    callback=self.parse_store
                )
            