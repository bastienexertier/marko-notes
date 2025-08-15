import re
from typing_extensions import override

from marko import block
from marko.helpers import MarkoExtension
from marko.source import Source

class Include(block.BlockElement):

	pattern: re.Pattern[str] = re.compile(r"::include\{file=(\S*)\}")

	def __init__(self, match: re.Match[str]) -> None:
		self.location: str = match.group(1)

	@classmethod
	@override
	def match(cls, source: Source) -> re.Match[str] | None:
		return source.expect_re(cls.pattern)

	@classmethod
	@override
	def parse(cls, source: Source) -> block.Document:
		with open(source.match.group(1)) as file:
			file_content = source.parser.parse(file.read())
		source.consume()
		return file_content



def make_extension() -> MarkoExtension:
	return MarkoExtension(
		elements=[Include],
		renderer_mixins=[]
	)
