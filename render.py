from collections.abc import Iterable
from pathlib import Path, PurePosixPath

from marko import Markdown
from marko.ext import codehilite, toc

import src.include_extension as include_extension
import src.note_extension as note_extension
import src.heading_section_extension as heading_section_extension
import src.jira_extension as jira_extension

def render_global_toc(files: Iterable[Path]) -> str:
	content = ['<ul>\n']
	depth = 0
	current_parent = Path()
	for file in files:

		parts = len(file.parts)-2

		if parts == depth:
			if file.parent != current_parent:
				current_parent = file.parent
				content.append(f'<a href="{file.name}">{file.parts[depth+1]}</a>\n')

		else:
			while parts > depth:
				content.append(f'<a href="{file.name}">{file.parts[depth+1]}</a>\n')
				content.append(f'<li>\n<ul>\n')
				depth += 1

			while parts < depth:
				content.append('</ul>\n</li>\n')
				depth -= 1

		content.append(f'<li><a href="{file.name}">{file.name}</a></li>\n')

	while depth > 0:
			content.append('</ul>\n</li>\n')
			depth -= 1

	content.append('</ul>')

	return str.join('', content)

def main(args) -> None:

	md = Markdown(
		extensions=[
			note_extension.make_extension(),
			include_extension.make_extension(),
			codehilite.make_extension(),
			heading_section_extension.make_extension(),
			jira_extension.make_extension(),
			toc.make_extension('<li><ul>', '</li></ul>'),
		]
	)

	md._setup_extensions()



	from jinja2 import Environment, FileSystemLoader
	env = Environment(loader=FileSystemLoader(searchpath="./"))
	template = env.get_template('markdown-base.html')

	root = Path('')
	notes = Path('notes')
	dist = Path('dist')

	markdown_files = sorted(notes.rglob('*.md'))

	global_toc = render_global_toc(markdown_files)

	for file in markdown_files:

		with file.open('r') as source_file:
			content = source_file.read()

		with md.parser.move(file.parent):
			doc = md.parse(content)

		text = md.render(doc)
		_toc = md.renderer.render_toc(maxdepth=4)

		output_filepath = dist/file

		output_filepath.parent.mkdir(exist_ok=True, parents=True)

		with output_filepath.with_suffix('.html').open('w', encoding='utf-8') as output:
			output.write(
				template.render(
					static=PurePosixPath(root).relative_to(output_filepath.parent, walk_up=True),
					global_toc='',
					body=text,
					toc=_toc.removeprefix('<li>').removesuffix('</li>'),
				)
			)

		# print(output_filepath)


if __name__ == '__main__':
	from argparse import ArgumentParser

	parser = ArgumentParser()

	main(parser.parse_args())
