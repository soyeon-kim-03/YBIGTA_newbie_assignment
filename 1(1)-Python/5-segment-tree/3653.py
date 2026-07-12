from lib import SegmentTree
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