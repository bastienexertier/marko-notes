
from pathlib import Path

from marko import Markdown
from marko.ext import codehilite, toc

import src.include_extension as include_extension
import src.note_extension as note_extension
import src.heading_section_extension as heading_section_extension



def main(args) -> None:

	md = Markdown(
		extensions=[
			note_extension.make_extension(),
			include_extension.make_extension(),
			codehilite.make_extension(),
			heading_section_extension.make_extension(),
			toc.make_extension('<li><ul>', '</li></ul>'),
		]
	)

	with args.file.open('r') as source_file:
		content = source_file.read()

	doc = md.parse(content)

	text = md.render(doc)
	_toc = md.renderer.render_toc()

	from jinja2 import Environment, FileSystemLoader
	env = Environment(loader=FileSystemLoader(searchpath="./"))
	template = env.get_template('markdown-base.html')

	with open('out.html', 'w') as output:
		output.write(template.render(body=text, toc=_toc.removeprefix('<li>').removesuffix('</li>')))

if __name__ == '__main__':
	from argparse import ArgumentParser

	parser = ArgumentParser()

	parser.add_argument('file', type=Path)

	main(parser.parse_args())
