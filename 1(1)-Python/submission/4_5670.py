from dataclasses import dataclass, field
from typing import TypeVar, Generic, Optional, Iterable


"""
TODO:
- Trie.push 구현하기
- (필요할 경우) Trie에 추가 method 구현하기
"""


T = TypeVar("T")


@dataclass
class TrieNode(Generic[T]):
    body: Optional[T] = None
    children: list[int] = field(default_factory=lambda: [])
    is_end: bool = False


class Trie(list[TrieNode[T]]):
    def __init__(self) -> None:
        super().__init__()
        self.append(TrieNode(body=None))

    def push(self, seq: Iterable[T]) -> None:
        """
        seq: T의 열 (list[int]일 수도 있고 str일 수도 있고 등등...)

        action: trie에 seq을 저장하기
        """
        pointer = 0
        for element in seq:
            node = self[pointer]
            next_index = None
            for child_idx in node.children:
                if self[child_idx].body == element:
                    next_index = child_idx
                    break
            if next_index is None:
                self.append(TrieNode(body=element))
                next_index = len(self) - 1
                node.children.append(next_index)
            pointer = next_index
        self[pointer].is_end = True


import sys


"""
TODO:
- 일단 Trie부터 구현하기
- count 구현하기
- main 구현하기
"""


def count(trie: Trie, query_seq: str) -> int:
    """
    trie - 이름 그대로 trie
    query_seq - 단어 ("hello", "goodbye", "structures" 등)

    returns: query_seq의 단어를 입력하기 위해 버튼을 눌러야 하는 횟수
    """
    pointer = 0
    cnt = 0

    for element in query_seq:
        if len(trie[pointer].children) > 1 or trie[pointer].is_end:
            cnt += 1

        new_index = -1
        for child_idx in trie[pointer].children:
            if trie[child_idx].body == element:
                new_index = child_idx
                break
        assert new_index != -1

        pointer = new_index

    return cnt + int(len(trie[0].children) == 1)


def main() -> None:
    input_data = sys.stdin.readline
    while True:
        line = input_data()
        if not line:
            break
        n = int(line)
        words = [input_data().strip() for _ in range(n)]

        trie: Trie[str] = Trie()
        for w in words:
            trie.push(w)

        total = sum(count(trie, w) for w in words)
        print(f"{total / n:.2f}")


if __name__ == "__main__":
    main()