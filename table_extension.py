
import re
from typing_extensions import override

from marko import MarkoExtension, block
from marko.source import Source
from .include_extension import Table, TableRow, TableHeader, TableData


class TableElement(block.BlockElement):

	pattern: re.Pattern[str] = re.compile(r"\|([^\|\n]*\|)+\n?")
	sep_pattern: re.Pattern[str] = re.compile(r"\|(-{3,}\|)+\n?")

	@classmethod
	@override
	def match(cls, source: Source) -> re.Match[str] | None:
		return source.expect_re(cls.pattern)

	@classmethod
	@override
	def parse(cls, source: Source) -> Table:

		headers = list[list[str]]()
		rows = list[list[str]]()

		while True:
			if source.expect_re(cls.sep_pattern):
				headers = rows
				rows = []
				source.consume()

			if source.expect_re(cls.pattern):	
				rows.append(source.match.group(0).split('|')[1:-1])
				source.consume()
			else:
				break

		return Table([
			TableRow([TableHeader(value.strip()) for value in row])
			for row in headers
		] + [
			TableRow([TableData(value.strip()) for value in row])
			for row in rows
		])


def make_extension() -> MarkoExtension:
	return MarkoExtension(
		elements=[TableElement],
	)