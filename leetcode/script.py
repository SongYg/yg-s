class Solution:
    def maxAreaOfIsland(self, grid: list) -> int:
        if len(grid) < 1:
            return 0

        def dfs(cur_i, cur_j):
            if cur_i < 0 or cur_i >= len(grid) or cur_j < 0 or cur_j >= len(grid[0]) or grid[cur_i][cur_j] == 0:
                return 0
            grid[cur_i][cur_j] = 0

            ans = 1
            for di, dj in [[1, 0], [-1, 0], [0, 1], [0, -1]]:
                next_i, next_j = cur_i + di, cur_j + dj
                ans += dfs(next_i, next_j)
            return ans

        max_area = 0
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                ans = dfs(i, j)
                max_area = max([max_area, ans])
        return max_area


s = Solution()
grid = [[0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0],
        [0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0],
        [0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0]]


res = s.maxAreaOfIsland(grid)
print(res)
