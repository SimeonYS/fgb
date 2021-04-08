import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import FfgbItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'
base = 'https://www.fgb.net/resources/blog/{}'

class FfgbSpider(scrapy.Spider):
	name = 'fgb'
	page = 1
	start_urls = [base.format(page)]

	def parse(self, response):
		post_links = response.xpath('//h3/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		if len(post_links) == 4:
			self.page += 1
			yield response.follow(base.format(self.page), self.parse)

	def parse_post(self, response):
		date = response.xpath('//div[@class="blog-details__date"]/text()').get()
		title = response.xpath('(//h1)[last()]/text()').get()
		content = response.xpath('//div[@class="blog-details__content"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=FfgbItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
