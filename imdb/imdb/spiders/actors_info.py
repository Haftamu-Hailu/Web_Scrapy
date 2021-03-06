# -*- coding: utf-8 -*-
import scrapy
import unidecode
import re
from elasticsearch import Elasticsearch
from ssl import create_default_context
import certifi
import uuid

context = create_default_context(cafile=certifi.where())
es = Elasticsearch(
    cloud_id="actors_db:dXMtZWFzdC0xLmF3cy5mb3VuZC5pbyQzYzFjNjZkN2Q4ZDk0NjkzYjg1YmRlNzhhY2I0ZjA0YyQzZWZmM2EyYWZiYTg0OWYyYTk4YzUzOGExNDU0NGY4ZQ==",
    http_auth=('elastic', '9YEFAqvb3aEQ2boBGeH9Ilda'),
    scheme="https",
    port=9243,
    ssl_context=context,
)
#remove all leading, trailing spaces, newline and brackets
cleanString = lambda x: '' if x is None else unidecode.unidecode(re.sub(r'^\s+|\s+$|\n|\(|\)','',x))


class ActorsInfoSpider(scrapy.Spider):
    name = 'actors_info'
    start_urls = ['https://www.imdb.com/title/tt0096463/fullcredits/']

    def parse(self, response):
        movie_name = response.css("div.subpage_title_block h3 a::text").get()
        if movie_name is None:
            movie_name = cleanString(response.css("div.title_wrapper h1::text").get())

        rating_value = response.css("div.ratingValue strong span::text").get()

        movie_year = cleanString(
                    response.css("div.subpage_title_block span.nobr::text").get()
        )
        if movie_year is None or movie_year is "":
            movie_year = response.css("div.title_wrapper h1 span a::text").get()

        movie_id = None
        if movie_year is not None and rating_value is not None:
            for meta in response.css("meta"):
                try: #not all the meta tags have attribute property
                    prop = meta.attrib['property']
                    if prop == "pageId":
                        movie_id = meta.attrib['content']
                except:
                    pass

            for tr in response.css("table.cast_list tr"):
                actor_name = cleanString(tr.css("a::text").get())
                if actor_name is not None and actor_name is not "": #some actor names are ""
                    role_name = cleanString(tr.css("td.character a::text").get())
                    if role_name is None or role_name is "": #sometimes role_name is ""
                        role_name = cleanString(tr.css("td.character::text").get())
                    actor_id = cleanString(tr.css("td.primary_photo a::attr(href)").get()).split('/')[2]
                    es.index(index='imdb',
                             doc_type='movies',
                             id=uuid.uuid4(),
                             body={
                                    'movie_id': movie_id,
                                    'movie_name': movie_name,
                                    'movie_year': int(movie_year),
                                    'movie_rating': float(rating_value),
                                    'actor_name': actor_name,
                                    'role_name': role_name,
                                    'actor_id': actor_id
                    })
        actor_page = response.css('table.cast_list tr td.primary_photo a::attr(href)').get()
        if actor_page is not None:
            actor_page = response.urljoin(actor_page)
            yield scrapy.Request(actor_page, callback=self.parse_actor)

    def parse_actor(self, response):
        print("parsing the actor page")
        for div in response.css("div.filmo-category-section div"):
            movie_year = cleanString(div.css("span.year_column::text").get())
            if "1979" < movie_year < "1990": #to do: remove spaces from strings
                in_production = div.css('a.in_production::text').get()
                if in_production is None:
                    movie_page = div.css("a::attr(href)").get()
                    if movie_page is not None:
                        movie_page = response.urljoin(movie_page)
                        yield scrapy.Request(movie_page, callback=self.parse)
