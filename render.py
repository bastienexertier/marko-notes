from collections.abc import Iterable
from pathlib import Path, PurePosixPath
import shutil

from marko import Markdown
from marko.ext import codehilite, toc

import src.prefix_tree as prefix_tree
import src.include_extension as include_extension
import src.note_extension as note_extension
import src.table_extension as table_extension

def main(args) -> None:

	md = Markdown(
		extensions=[
			note_extension.make_extension(),
			include_extension.make_extension(),
			codehilite.make_extension(),
			toc.make_extension('<li><ul>', '</li></ul>'),
			table_extension.make_extension(),
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

	tree = prefix_tree.Tree(md_file.with_suffix('').parts for md_file in markdown_files)

	res = list[str]()
	res.append('<ul>')

	for element in tree:
		match element:
			case prefix_tree.Down(v):
				res.append('<li class="_expand">')
				res.append(str(v).replace('-', ' ').title())
				res.append('<ul>')
			case prefix_tree.Up():
				res.append('</ul>')
				res.append('</li>')
			case v:
				res.append('<li class="_expand">')
				res.append(f'<a href="{Path(dist, *v).with_suffix(".html").absolute().as_uri()}">')
				res.append(v[-1].removesuffix('.md').replace('-', ' ').title())
				res.append('</a>')
				res.append('</li>')

	res.append('</ul>')

	global_toc = str.join('\n', res)

	# global_toc = render_global_toc(markdown_files)

	for file in args.files or notes.rglob('*'):

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
					title=file.stem.replace('-', ' ').title(),
					static=root.absolute().as_uri(),
					global_toc=global_toc,
					body=text,
					toc=_toc.removeprefix('<li>').removesuffix('</li>'),
				)
			)


if __name__ == '__main__':
	from argparse import ArgumentParser

	parser = ArgumentParser()

	parser.add_argument('files', default=None, nargs='*', type=Path)

	main(parser.parse_args())
