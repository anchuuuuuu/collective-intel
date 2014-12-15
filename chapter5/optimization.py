# -*- coding: utf-8 -*-
import math
import time
import random
import math

people = [
            ('Seymour','BOS'),
            ('Franny','DAL'),
            ('Zooey','CAK'),
            ('Walt','MIA'),
            ('Buddy','ORD'),
            ('Les','OMA')
            ]
destination = 'LGA'
flights = {}

# 5.1 - Introduction
for line in file('schedule.txt'):
    origin, dest, depart, arrive, price = line.strip( ).split(',') #----> demo.dic()
    flights.setdefault((origin,dest), [])

    flights[(origin, dest)].append((depart, arrive, int(price)))

def getminutes(t):
    x = time.strptime(t, '%H:%M')
    return x[3] * 60 + x[4]

# 5.2 - Represent solution
def printschedule(r):
    for d in range(len(r) / 2): # r = [4,4,4,2,2,6,6,5,5,6,6,0] e.g. 
        name = people[d][0]
        origin = people[d][1]
        out = flights[(origin, destination)][int(r[d * 2])]
        ret = flights[(destination, origin)][int(r[d * 2 + 1])] # [4,4,4,2,2,6,6,5,-,-,6,0] <- [4 * 2] & [4 * 2 + 1]

        print '%10s%10s %5s-%5s $%d %5s-%5s $%3s' % (name, origin, out[0], out[1], out[2], ret[0], ret[1], ret[2])

# 5.3 - Cost Function
def schedulecost(sol):
    totalprice = 0
    latestarrival = 0
    earliestdep = 24 * 60

    for d in range(len(sol) / 2):
        origin = people[d][1]
        outbound = flights[(origin, destination)][int(sol[d * 2])]        
        returnf = flights[(destination, origin)][int(sol[d * 2 + 1])]        
        
        totalprice += outbound[2]
        totalprice += returnf[2]
        
        if latestarrival < getminutes(outbound[1]): latestarrival = getminutes(outbound[1])
        if earliestdep > getminutes(returnf[0]): earliestdep = getminutes(returnf[0])

    totalwait = 0
    for d in range(len(sol) / 2):
        origin = people[d][1]
        outbound = flights[(origin, destination)][int(sol[d * 2])]
        returnf  = flights[(destination, origin)][int(sol[d * 2 + 1])]
        totalwait += math.fabs(latestarrival - getminutes(outbound[1]))
        totalwait += math.fabs(getminutes(returnf[0]) - earliestdep)

    if latestarrival < earliestdep: totalprice += 50

#    print "total wait  : ", str(totalwait)
#    print "total price : ", str(totalprice)

    return totalprice + totalwait

# 5.4 - Random Search
def randomoptimize(domain, costf):
    best  = 99999999
    bestr = None
    for i in range(1000):
        r = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]
        
        cost = costf(r)

        if cost < best:
            best = cost
            bestr = r
            print "BEST SCORE :", best
    return bestr
    
    
    
# 5.5 - Hill Climb
def hillclimb(domain, costf):

    sol = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]

    while 1:
        neighbors = []

        for j in range(len(domain)):
            # 各方向に解を１つずつずらす
            # 0~8の範囲外に出ないように注意
            # なぜなら[0,0,0,0,0,0,0,9] ←はあり得ないので
            if sol[j] > domain[j][0]:
                neighbors.append(sol[0:j] + [sol[j] - 1] + sol[j + 1:])
            if sol[j] < domain[j][1]:
                neighbors.append(sol[0:j] + [sol[j] + 1] + sol[j + 1:])

                #e.g. [5,5,5,5,5,5,5,5]で, j==2 の場合
                #     [5,5] + [4] + [5,5,5,5,5]
                #     [5,5] + [6] + [5,5,5,5,5]

                #     [5,5,4,5,5,5,5,5]
                #     [5,5,6,5,5,5,5,5]
                
        # 上のforループに入る前のベスト解を current, best に代入
        current = costf(sol)
        best = current
        
        for j in range(len(neighbors)):
            cost = costf(neighbors[j])

            if cost < best:
                best = cost
                sol = neighbors[j]

        if best == current:
            break

    return sol


# 5.6 - Simulated Annealing (Yakinamashi method)
def annealingoptimize(domain, costf, T= 10000.0, cool = 0.95, step=1):
    vec = [float(random.randint(domain[i][0],  domain[i][1])) for i in range(len(domain)) ]
   
   
    # 温度の初期値は 10000.0度。 0.1度に下がるまで解を探す
    while T > 0.1:

        # 解[0,0,0,0,0,0,0,0]のランダム位置を、-1/+0/+1したい
        i = random.randint(0, len(domain) - 1) # i = ランダム位置
        dir=random.randint(-step, step) # -1, +0, +1 のどれか
        vecb = vec[:] # リストを複製
        vecb[i] += dir # 解の位置 i 部分を, -1/+0/+1 した

        if vecb[i] < domain[i][0]: vecb[i] = domain[i][0] # 0未満は0
        elif vecb[i] > domain[i][1]: vecb[i] = domain[i][1] # 8を超えたら8

        ea = costf(vec)
        eb = costf(vecb)
        p  = pow(math.e, -abs(eb - ea) / T)

        # eb < ea               コストが低い場合はそのまま採択
        # random.random() < p   コストが高くても、exp(-δ/T) の確率で採択
        if (eb < ea or random.random() < p):
            vec = vecb

        # 温度T を下げる。0.95をかけることで0に近づける
        T = T * cool

    return vec

# 5.7 - Genetic Optimize
def geneticoptimize(domain, costf, popsize = 50, step = 1, mutprob = 0.2, elite = 0.2, maxiter = 100):
    # 突然変異の割合は20%, 次世代まで生き残れるエリート個体は20%, 個体数は50, 世代は100
    
    def mutate(vec): # 突然変異
        i = random.randint(0, len(domain) - 1) # ランダム位置 i の決定
        if random.random() < 0.5 and vec[i] > domain[i][0]: # 50%の確率で、位置iの要素を減少
            return vec[0:i] + [vec[i] - step] + vec[i + 1:]
        elif vec[i] < domain[i][1]:
            return vec[0:i] + [vec[i] + step] + vec[i + 1:] # 50%の確率で、位置iの要素を増加

    def crossover(r1, r2): # 交叉
        i = random.randint(1, len(domain) - 2) # ランダム位置 i の決定
        return r1[0:i] + r2[i:]

    pop = [] # ランダム解のためのリスト

    for i in range(popsize): # popsize分だけ、ランダムな解を生成（初回のみ）
        vec = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]
        pop.append(vec)

    topelite = int(elite * popsize) # topelite: 次の世代に生き残れる数

    for i in range(maxiter):
        scores = [(costf(v), v) for v in pop if v != None] # 各解のスコアを計算, リストに保存
        scores.sort() # 第一要素(スコア)でソート
        ranked = [v for (s, v) in scores] # ランク情報のリストを作成

        pop = ranked[0:topelite]

        while len(pop) < popsize:

            # 20%は突然変異。エリート個体の遺伝子を突然変異させる
            if random.random() < mutprob:
                c = random.randint(0, topelite)
                pop.append(mutate(ranked[c]))

            # 残りの80%はエリート個体同士を交叉
            else:
                c1 = random.randint(0, topelite)
                c2 = random.randint(0, topelite)
                pop.append(crossover(ranked[c1], ranked[c2]))

        print scores[0][0]

    return scores[0][1]

