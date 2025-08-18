import re
from contextlib import contextmanager
from pathlib import Path
from typing_extensions import override

from marko import block
from marko.element import Element
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

class Include(block.BlockElement):

	pattern: re.Pattern[str] = re.compile(r"::include\{file=([^\s#\}]+)\}")

	@classmethod
	@override
	def match(cls, source: Source) -> re.Match[str] | None:
		return source.expect_re(cls.pattern)

	@classmethod
	@override
	def parse(cls, source: Source) -> block.Document:
		location = source.match.group(1)

		if location[0] == '/':
			file_path = source.parser.base_path() / location.removeprefix('/')
		else:
			file_path = source.parser.path() / location

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
		elements=[Include],
		parser_mixins=[ParserMixin],
		renderer_mixins=[],
	)
