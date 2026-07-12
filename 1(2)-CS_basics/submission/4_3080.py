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
- 일단 lib.py의 Trie Class부터 구현하기
- main 구현하기

힌트: 한 글자짜리 자료에도 그냥 str을 쓰기에는 메모리가 아깝다...
"""
MOD = 1000000007
MAX_N = 3001

def main() -> None:
    # 구현하세요!
    input_data = sys.stdin.readline
    n = int(input_data())
    names = [input_data().strip() for _ in range(n)]

    trie: Trie[str] = Trie()
    for name in names:
        trie.push(name)

    fact = [1] * (MAX_N + 1)
    for i in range(1, MAX_N + 1):
        fact[i] = fact[i - 1] * i % MOD
    inv_fact = [1] * (MAX_N + 1)
    inv_fact[MAX_N] = pow(fact[MAX_N], MOD - 2, MOD)
    for i in range(MAX_N, 0, -1):
        inv_fact[i - 1] = inv_fact[i] * i % MOD

    size = [0] * len(trie)
    ways = [1] * len(trie)

    for idx in range(len(trie) - 1, -1, -1):
        node = trie[idx]
        total = 1 if node.is_end else 0
        numerator = 1
        denom_inv = 1
        for child_idx in node.children:
            total += size[child_idx]
            numerator = numerator * ways[child_idx] % MOD
            denom_inv = denom_inv * inv_fact[size[child_idx]] % MOD
        size[idx] = total
        ways[idx] = fact[total] * denom_inv % MOD * numerator % MOD

    print(ways[0])


if __name__ == "__main__":
    main()