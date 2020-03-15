# Python实现
class Solution:
    def maxPerformance(self, n: int, speed: list, efficiency: list, k: int) -> int:
        MOD = int(10 ** 9 + 7)
        team = [[speed[i], efficiency[i]] for i in range(n)]
        team.sort(key=lambda x: (x[1], x[0]), reverse=True)
        from queue import PriorityQueue
        pq = PriorityQueue()
        speedSum = 0
        maxPerf = 0

        for i in range(n):
            if i < k:
                pq.put(team[i][0])
                speedSum += team[i][0]
                maxPerf = max([maxPerf, speedSum * team[i][1]])
            else:
                if team[i][0] > pq.queue[0]:
                    speed_ = pq.get()
                    pq.put(team[i][0])
                    speedSum = speedSum - speed_ + team[i][0]
                    maxPerf = max([maxPerf, speedSum * team[i][1]])

        return maxPerf % MOD


s = Solution()
n = 6
speed = [10, 5, 1, 7, 4, 2]
efficiency = [2, 1, 1, 1, 7, 3]
k = 6

res = s.maxPerformance(n, speed, efficiency, k)
print(res)
