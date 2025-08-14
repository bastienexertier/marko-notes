
from pathlib import Path

from marko import Markdown, Renderer
from marko.ext import codehilite

import include_extension
import note_extension
import heading_section_extension


# class CustomRenderer(Renderer):

# 	def render_heading(self, element):
# 		return f'<section>{self.render_children(element)}</section>'


def main(args) -> None:

	# from rich import inspect
	# inspect(Renderer, all=True)

	md = Markdown(
		# renderer=CustomRenderer,
		extensions=[
			note_extension.make_extension(),
			include_extension.make_extension(),
			codehilite.make_extension(),
			heading_section_extension.make_extension(),
		]
	)

	with args.file.open('r') as source_file:
		content = source_file.read()

	doc = md.parse(content)

	# print(doc)

	text = md.render(doc)

	# print(text)

	from jinja2 import Environment, FileSystemLoader
	env = Environment(loader=FileSystemLoader(searchpath="./"))
	template = env.get_template('markdown-base.html')

	with open('out.html', 'w') as output:
		output.write(template.render(body=text))

if __name__ == '__main__':
	from argparse import ArgumentParser

	parser = ArgumentParser()

	parser.add_argument('file', type=Path)

	main(parser.parse_args())