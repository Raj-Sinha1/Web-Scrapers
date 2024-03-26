import scrapy
import pycountry
import json

class pancakeSpider(scrapy.Spider):
    name='99pancakes_ind_dpa'
    brand_name="99pancakes"
    spider_type="chain"
    # spider_chain_id="34158"
    # spideder_categories=[Code.RENTAL_CAR_AGENCY.value]
    spider_countries=[pycountry.countries.lookup('ind').alpha_3]

    allowed_domains = ['https://storelocator.metizapps.com/stores/storeDataGet']

    def start_requests(self):

        form_data={
            'shopData':"99-pancakes.myshopify.com"
        }
        
        url='https://storelocator.metizapps.com/stores/storeDataGet'

        yield scrapy.FormRequest(
            url=url,
            formdata=form_data,
            callback=self.parse
        )
    
    def parse(self, response):
        '''
        @url https://api.zoomcar.com/v5/countries?platform=web&version=2&device_id=057ec5a5-af34-42e2-ba2c-1756060bdcc2 
        '''

        my_data=json.loads(response.text)

        for i in my_data['data']['result']:
            data={

                "ref: ":i['id'],
                'chain_name':"99pancakes",
                'chain_id':"34158",
                "name:": i['storename'],
                'brand':"99pancakes",
                "Address: ":i['address']+" "+i['address2']+" "+i['cityname']+": "+i['statename']+" "+i['zipcode']+": "+i['countryname'],
                "city:": i['cityname'],
                "state:": i['statename'],
                "postcode:": i['zipcode'],
                "country:": i['countryname'],
                "Phone:": i['phone'],
                "website:":'https://99pancakes.in',
                "latitude:": i['mapLatitude'],
                "Longitude:": i['mapLongitude'],
            }

                # yield GeojsonPointItem(**data)
            yield data