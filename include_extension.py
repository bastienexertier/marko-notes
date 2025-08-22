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
		self.__paths: list[Path] = [Path('notes')]

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
		self.inline_body = value

class TableData(block.BlockElement):
	virtual = True

	def __init__(self, value: str) -> None:
		self.inline_body = value

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

class Mermaid(block.BlockElement):
	virtual = True

	def __init__(self, content: str) -> None:
		self.content = content
		

class IncludeMermaid(IncludeBase):

	pattern: re.Pattern[str] = re.compile(r"::include\{file=([^\s\}\.]+\.mermaid)\}")

	@classmethod
	@override
	def parse(cls, source: Source) -> Mermaid:

		file_path = cls.get_location(source)
		with file_path.open('r', encoding='utf-8') as file:
			mermaid = Mermaid(file.read())

		source.consume()
		return mermaid

class MermaidRenderer(Renderer):

	def render_mermaid(self, element: Mermaid) -> str:
		return f'<pre class="mermaid">{element.content}</pre>'

class IncludePicture(IncludeBase):

	pattern: re.Pattern[str] = re.compile(r"::include\{file=([^\s\}\.]+\.(png|jpg))\}")

	def __init__(self, location: Path) -> None:
		self.location = location

	@classmethod
	@override
	def parse(cls, source: Source):
		file_path = cls.get_location(source)
		source.consume()
		return file_path.absolute()

class PictureRenderer:

	def render_include_picture(self, element: IncludePicture) -> str:
		return f'<img src="{element.location}" />'

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

class Define(block.BlockElement):

	pattern: re.Pattern[str] = re.compile(r"::define\{([\w\-\_]+)=([^\n\}]*)\}")

	variables: dict[str, block.BlockElement] = {}

	def __init__(self, value: str) -> None:
		self.inline_body = value

	@classmethod
	@override
	def match(cls, source: Source) -> re.Match[str] | None:
		return source.expect_re(cls.pattern)

	@classmethod
	@override
	def parse(cls, source: Source):
		name = source.match.group(1)
		value = source.match.group(2)
		element = cls(value)
		cls.variables[name] = element
		source.consume()
		return element


class Interpolation(inline.InlineElement):

	pattern: re.Pattern[str] = re.compile(r"\$([\w\-\_]+)")

	def __init__(self, match: re.Match[str]) -> None:
		self.children = Define.variables[match.group(1)].children


class InterpolationRenderer:

	def render_define(self, element: Define) -> str:
		return ''

	def render_interpolation(self, element: Interpolation) -> str:
		return self.render_children(element)


def make_extension() -> MarkoExtension:
	return MarkoExtension(
		elements=[IncludeCsv, IncludeMermaid, IncludePicture, Include, Define, Interpolation],
		parser_mixins=[ParserMixin],
		renderer_mixins=[TableRenderer, MermaidRenderer, PictureRenderer, InterpolationRenderer],
	)
