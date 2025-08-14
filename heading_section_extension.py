
from marko import block
from marko.helpers import MarkoExtension

class HeadingRenderer:

	def render_heading(self, element: block.Heading) -> str:
		section_id = self.render_children(element).replace(' ', '-')
		return f'<section id="{section_id}">{super().render_heading(element)}</section>'

def make_extension() -> MarkoExtension:
	return MarkoExtension(
		elements=[],
		renderer_mixins=[HeadingRenderer]
	)
