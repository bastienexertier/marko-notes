import csv
import re
from contextlib import contextmanager
from pathlib import Path
from typing_extensions import override

from marko import Renderer, block, inline
from marko.helpers import MarkoExtension
from marko.source import Source

class ParserMixin:

	def __init__(self):
		super().__init__()
		self.__paths: list[Path] = [Path()]

	def path(self) -> Path:
		return self.__paths[-1]

	def base_path(self) -> Path:
		return self.__paths[0]

	@contextmanager
	def move(self, new_path: str):
		self.__paths.append(Path(new_path))
		yield self
		self.__paths.pop(-1)

class IncludeBase(block.BlockElement):

	pattern: re.Pattern[str] = re.compile(r"::include\{file=([^\s#\}]+)\}")

	@classmethod
	@override
	def match(cls, source: Source) -> re.Match[str] | None:
		return source.expect_re(cls.pattern)

	@classmethod
	def get_location(cls, source: Source) -> Path:

		location = source.match.group(1)

		if location[0] == '/':
			return source.parser.base_path() / location.removeprefix('/')

		return source.parser.path() / location


class TableHeader(block.BlockElement):
	virtual = True

	def __init__(self, value: str) -> None:	
		self.children = [inline.RawText(value)]

class TableData(block.BlockElement):
	virtual = True

	def __init__(self, value: str) -> None:	
		self.children = [inline.RawText(value)]

class TableRow(block.BlockElement):
	virtual = True

	def __init__(self, cells: list[TableHeader]|list[TableData]) -> None:
		self.children = cells

class Table(block.BlockElement):
	virtual = True

	def __init__(self, rows: list[TableRow]) -> None:
		self.children = rows

class IncludeCsv(IncludeBase):

	pattern: re.Pattern[str] = re.compile(r"::include\{file=([^\s\}\.]+\.csv)\}")

	def __init__(self, rows: list[block.BlockElement]) -> None:
		self.children = rows

	@classmethod
	@override
	def parse(cls, source: Source) -> Table:

		file_path = cls.get_location(source)

		row_elements = []

		with file_path.open('r', encoding='utf-8') as file:
			rows = csv.reader(file, delimiter=';')
			for index, row in enumerate(rows):
				if index == 0:
					cells = [TableHeader(value) for value in row]
				else:
					cells = [TableData(value) for value in row]

				row_elements.append(TableRow(cells))

		source.consume()

		return Table(row_elements)


class TableRenderer(Renderer):

	def render_table_header(self, element: TableHeader) -> str:
		return f'<th>{self.render_children(element)}</th>'

	def render_table_data(self, element: TableData) -> str:
		return f'<td>{self.render_children(element)}</td>'

	def render_table_row(self, element: TableRow) -> str:
		return f'<tr>{self.render_children(element)}</tr>'

	def render_table(self, element: Table) -> str:
		return f'<table>{self.render_children(element)}</table>'

		

class Include(IncludeBase):

	@classmethod
	@override
	def parse(cls, source: Source) -> block.Document:

		file_path = cls.get_location(source)

		if file_path.suffix == '.md':
			template = '{content}'
		else:
			template = '```{extension}\n{content}\n```'

		with file_path.open('r', encoding='utf-8') as file:
			with source.parser.move(file_path.parent):
				document = source.parser.parse(
					template.format(extension=file_path.suffix[1:], content=file.read())
				)

		source.consume()

		return document



def make_extension() -> MarkoExtension:
	return MarkoExtension(
		elements=[IncludeCsv, Include],
		parser_mixins=[ParserMixin],
		renderer_mixins=[TableRenderer],
	)
