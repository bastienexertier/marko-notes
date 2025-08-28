
from dataclasses import dataclass
from typing import Iterable, Iterator, Union

@dataclass
class Down:
	value: str
	def __repr__(self) -> str: return f'DOWN<{self.value}>'

@dataclass
class Up:
	def __repr__(self) -> str: return 'UP'


V = tuple[str, ...]

class Tree:

	def __init__(self, data: Iterable[tuple[str, ...]]) -> None:
		self.node = Node('')
		for value in data:
			self.add_value(value)

	def __len__(self) -> int:
		return self.node.__len__()

	def __iter__(self) -> Iterator[Union[Up, Down, V]]:
		return self.node.walk(0)

	def add_value(self, value: V) -> None:

		current = self.node

		for index, part in enumerate(value):

			if index == len(value)-1:
				current.members.append(value)
				break

			if not (next_node := current.children.get(part)):
				next_node = Node(part)
				current.children[part] = next_node

			current = next_node


class Node:

	def __init__(self, value: str) -> None:
		self.value = value
		self.members = list[V]()
		self.children = dict[str, Node]()

	def __str__(self) -> str:
		return f'Node({self.value})'

	def __len__(self) -> int:
		return len(self.members) + sum(len(child) for child in self.children.values())

	def walk(self, height: int) -> Iterator[Union[Up, Down, V]]:

		for member in self.members:
			yield member

		for name, child in self.children.items():
			yield Down(name)
			yield from child.walk(height+1)
			yield Up()
