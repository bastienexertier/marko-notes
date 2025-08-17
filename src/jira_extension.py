from os import stat
import re
from contextlib import contextmanager
from pathlib import Path
from typing_extensions import override

from marko import inline
from marko.element import Element
from marko.helpers import MarkoExtension
from marko.source import Source


class JiraLink(inline.InlineElement):

	pattern: re.Pattern[str] = re.compile(r"#jira:(\w+-\d+)")

	def __init__(self, match: re.Match):
		self.key = match.group(1)

	@classmethod
	@override
	def match(cls, source: Source) -> re.Match[str] | None:
		return source.expect_re(cls.pattern)

	@classmethod
	@override
	def parse(cls, source: Source):
		return cls(source.match)



class JiraLinkRenderer:

	def render_jira_link(self, element: JiraLink) -> str:
		return f'<a href="">{element.key}</a>'


def make_extension() -> MarkoExtension:
	return MarkoExtension(
		elements=[JiraLink],
		renderer_mixins=[JiraLinkRenderer],
	)
