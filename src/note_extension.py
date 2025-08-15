import re

from marko import Markdown, inline, block
from marko.helpers import MarkoExtension
from marko.source import Source

class Note(block.BlockElement):

	priority = 7
	_prefix = r" {,3}>[^\n\S]?"

	pattern: re.Pattern = re.compile(r" {,3}>\s+\[!(NOTE|TIP|IMPORTANT|CAUTION|WARNING)\]\s+(.*)", re.IGNORECASE)

	def __init__(self, match: re.Match[str]) -> None:
		self.note_type = match.group(1)
		self.title = match.group(2)

	@classmethod
	def match(cls, source: Source) -> re.Match[str] | None:
		return source.expect_re(cls.pattern)

	@classmethod
	def parse(cls, source: Source) -> 'Note':
		note = cls(source.match)
		with source.under_state(note) as n_source:
			source.pos = source.match.end() + 1
			note.children = source.parser.parse_source(source)
		return note


class NoteRenderer:

	def render_note(self, element: Note) -> str:
		return f'''
<div class="admonition {element.note_type.lower()}">
	<p class="admonition-title">{element.title or element.note_type.upper()}</p>
	{self.render_children(element)}
</div>
'''


def make_extension():
	return MarkoExtension(
		elements=[Note],
		renderer_mixins=[NoteRenderer]
	)
