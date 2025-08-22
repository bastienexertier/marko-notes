from collections.abc import Iterable
from pathlib import Path, PurePosixPath
import shutil

from marko import Markdown
from marko.ext import codehilite, toc

import src.include_extension as include_extension
import src.note_extension as note_extension
import src.heading_section_extension as heading_section_extension
import src.jira_extension as jira_extension
import src.table_extension as table_extension
import src.strikethrough_extension as strikethrough_extension

def render_global_toc_(files: Iterable[Path]) -> str:

	for file in files:
		pass

def common_prefix(p1: Path, p2: Path) -> int:
	p1_parts = p1.parts
	p2_parts = p2.parts
	for i in range(min(len(p1_parts), len(p2_parts))):
		if p1_parts[i] != p2_parts[i]:
			break
	return i

def render_global_toc(files: Iterable[Path]) -> str:
	content = ['<ul>\n']
	depth = 0
	prev = Path()
	for file in files:

		parts = len(file.parts)-2

		if parts == depth:
			if file.parent != prev.parent:
				depth = common_prefix(file.parent, prev.parent)
				content.append(f'<a href="{file.name}">{file.parts[depth+1]}</a>\n')

		else:
			while parts > depth:
				content.append(f'<a href="{file.name}">{file.parts[depth+1]}</a>\n')
				content.append(f'<li>\n<ul>\n')
				depth += 1

			while parts < depth:
				content.append('</ul>\n</li>\n')
				depth -= 1

		prev = file
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
			table_extension.make_extension(),
			strikethrough_extension.make_extension(),
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

	for file in notes.rglob('*'):

		if file.is_dir():
			continue

		output_filepath = dist / file
		output_filepath.parent.mkdir(exist_ok=True, parents=True)

		if file.suffix != '.md':
			if not output_filepath.exists():
				shutil.copy(file, output_filepath)
			continue

		with file.open('r', encoding='utf-8') as source_file:
			content = source_file.read()

		with md.parser.move(file.parent):
			doc = md.parse(content)

		text = md.render(doc)
		_toc = md.renderer.render_toc(maxdepth=4)


		with output_filepath.with_suffix('.html').open('w', encoding='utf-8') as output:
			_ = output.write(
				template.render(
					static=PurePosixPath(root).relative_to(output_filepath.parent, walk_up=True),
					# global_toc=global_toc,
					body=text,
					toc=_toc.removeprefix('<li>').removesuffix('</li>'),
				)
			)

		# print(output_filepath)


if __name__ == '__main__':
	from argparse import ArgumentParser

	parser = ArgumentParser()

	main(parser.parse_args())
