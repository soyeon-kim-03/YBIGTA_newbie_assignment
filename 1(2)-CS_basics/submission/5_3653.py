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


def main() -> None:
    # 구현하세요!
    data = sys.stdin.read().split()
    idx = 0
    t = int(data[idx]); idx += 1
    outputs = []

    for _ in range(t):
        n, m = int(data[idx]), int(data[idx + 1]); idx += 2
        queries = data[idx: idx + m]
        idx += m

        size = n + m
        tree: SegmentTree[int, int] = SegmentTree(
            size,
            default=lambda: 0,
            f_conv=lambda x: x,
            f_merge=lambda a, b: a + b,
        )

        pos = [0] * (n + 1)
        for movie in range(1, n + 1):
            position = m + movie
            pos[movie] = position
            tree.add(position, 1)

        top = m  # 다음에 놓일 자리 (m부터 1까지 줄어듦)
        results = []
        for q in queries:
            movie = int(q)
            p = pos[movie]
            above = tree.query(1, p - 1) if p > 1 else 0
            results.append(above)

            tree.add(p, -1)
            tree.add(top, 1)
            pos[movie] = top
            top -= 1

        outputs.append(" ".join(map(str, results)))

    sys.stdout.write("\n".join(outputs) + "\n")



if __name__ == "__main__":
    main()