from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeVar, Generic, Optional, Callable


"""
TODO:
- SegmentTree 구현하기
"""


T = TypeVar("T")
U = TypeVar("U")


class SegmentTree(Generic[T, U]):
    # 구현하세요!
    def __init__(
        self,
        n: int,
        default: Callable[[], U],
        f_conv: Callable[[T], U],
        f_merge: Callable[[U, U], U],
    ) -> None:
        """
        n: 원소 개수
        default: 항등원(빈 구간 결과값)을 만드는 함수
        f_conv: 원본 값(T)을 트리 저장값(U)으로 바꾸는 함수
        f_merge: 두 U를 하나로 합치는 연산
        """
        self.n = n
        self.default = default
        self.f_conv = f_conv
        self.f_merge = f_merge

        self.size = 1
        while self.size < n:
            self.size *= 2

        self.tree: list[U] = [default() for _ in range(2 * self.size)]

    def update(self, index: int, value: T) -> None:
        """index(1-based) 위치의 값을 value로 덮어쓴다."""
        i = index - 1 + self.size
        self.tree[i] = self.f_conv(value)
        i //= 2
        while i >= 1:
            self.tree[i] = self.f_merge(self.tree[2 * i], self.tree[2 * i + 1])
            i //= 2

    def add(self, index: int, delta: T) -> None:
        """index(1-based) 위치의 값에 delta를 누적(병합)한다."""
        i = index - 1 + self.size
        self.tree[i] = self.f_merge(self.tree[i], self.f_conv(delta))
        i //= 2
        while i >= 1:
            self.tree[i] = self.f_merge(self.tree[2 * i], self.tree[2 * i + 1])
            i //= 2

    def query(self, left: int, right: int) -> U:
        """[left, right] (1-based, 양끝 포함) 구간 병합 결과를 반환한다."""
        l = left - 1 + self.size
        r = right - 1 + self.size
        res_l = self.default()
        res_r = self.default()
        while l <= r:
            if l % 2 == 1:
                res_l = self.f_merge(res_l, self.tree[l])
                l += 1
            if r % 2 == 0:
                res_r = self.f_merge(self.tree[r], res_r)
                r -= 1
            l //= 2
            r //= 2
        return self.f_merge(res_l, res_r)

    def find_kth(self, k: int) -> int:
        """
        leaf 값을 '개수'로 볼 때, 누적합이 k를 처음 넘는 위치(1-based)를 찾는다.
        (2243, 3653처럼 U가 int(개수)인 경우 사용)
        """
        node = 1
        while node < self.size:
            left_child = 2 * node
            left_count = self.tree[left_child]
            if k <= left_count:  # type: ignore[operator]
                node = left_child
            else:
                k -= left_count  # type: ignore[operator]
                node = left_child + 1
        return node - self.size + 1


import sys


"""
TODO:
- 일단 SegmentTree부터 구현하기
- main 구현하기
"""


class Pair(tuple[int, int]):
    """
    힌트: 2243, 3653에서 int에 대한 세그먼트 트리를 만들었다면 여기서는 Pair에 대한 세그먼트 트리를 만들 수 있을지도...?
    """
    def __new__(cls, a: int, b: int) -> 'Pair':
        return super().__new__(cls, (a, b))

    @staticmethod
    def default() -> 'Pair':
        """
        기본값
        이게 왜 필요할까...?
        """
        return Pair(0, 0)

    @staticmethod
    def f_conv(w: int) -> 'Pair':
        """
        원본 수열의 값을 대응되는 Pair 값으로 변환하는 연산
        이게 왜 필요할까...?
        """
        return Pair(w, 0)

    @staticmethod
    def f_merge(a: Pair, b: Pair) -> 'Pair':
        """
        두 Pair를 하나의 Pair로 합치는 연산
        이게 왜 필요할까...?
        """
        return Pair(*sorted([*a, *b], reverse=True)[:2])

    def sum(self) -> int:
        return self[0] + self[1]


def main() -> None:
    # 구현하세요!
    input_data = sys.stdin.readline
    n = int(input_data())
    arr = list(map(int, input_data().split()))

    tree: SegmentTree[int, Pair] = SegmentTree(
        n,
        default=Pair.default,
        f_conv=Pair.f_conv,
        f_merge=Pair.f_merge,
    )
    for i, v in enumerate(arr, start=1):
        tree.update(i, v)

    m = int(input_data())
    results = []
    for _ in range(m):
        cmd, x, y = map(int, input_data().split())
        if cmd == 1:
            tree.update(x, y)
        else:
            results.append(tree.query(x, y).sum())

    sys.stdout.write("\n".join(map(str, results)) + "\n")


if __name__ == "__main__":
    main()