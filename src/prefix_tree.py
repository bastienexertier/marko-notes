
from dataclasses import dataclass
from typing import Iterable, Iterator, Optional, Union

V = tuple[str, ...]

@dataclass
class Down:
	name: str
	value: Optional[V]

@dataclass
class Up:
	...

class Tree:

	def __init__(self, data: Iterable[tuple[str, ...]]) -> None:
		self.node = Node(())
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
				next_node = Node(value[:index+1])
				current.children[part] = next_node

			current = next_node


class Node:

	def __init__(self, value: V) -> None:
		self.value = value
		self.members = list[V]()
		self.children = dict[str, Node]()

	def __str__(self) -> str:
		return f'Node({self.value})'

	def __len__(self) -> int:
		return len(self.members) + sum(len(child) for child in self.children.values())

	def walk(self, height: int) -> Iterator[Union[Up, Down, V]]:

		for member in self.members:
			if not is_main_element(member):
				yield member

		for name, child in self.children.items():
			main_element = next(filter(is_main_element, child.members), None)
			yield Down(name, main_element)
			yield from child.walk(height+1)
			yield Up()

def is_main_element(element: V) -> bool:
	return len(element) >= 2 and element[-1] == element[-2]
