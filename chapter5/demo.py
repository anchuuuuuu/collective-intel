import math
import time
import random
import math
import sys

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

# DEMO 5.1 - Introduction
def dic():
    for line in file('schedule.txt'):
        print "ORIGINAL LINE"
        print line

        print ">line.strip()"
        print line.strip( )

        print ""
        print ">line.strip( ).split(',')"
        origin, dest, depart, arrive, price = line.strip( ).split(',')    
        print origin, dest, depart, arrive, price

        flights.setdefault((origin,dest), [])

        flights[(origin, dest)].append((depart, arrive, int(price)))
        break

# DEMO 5.4 - Random Search
def randomsearch():
    domain = [(0,8)] * (len(people)*2)
    
    print "random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]"
    r = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]
    print r
    


def getminutes(t):
    x = time.strptime(t, '%H:%M')
    return x[3] * 60 + x[4]

# 5.2 - Represent solution
def printschedule(r):
    for d in range(len(r) / 2):
        name = people[d][0]
        origin = people[d][1]
        out = flights[(origin, destination)][int(r[d * 2])]
        ret = flights[(destination, origin)][int(r[d * 2 + 1])]
        print '%10s%10s %5s-%5s $%d %5s-%5s $%3s' % (name, origin, out[0], out[1], out[2], ret[0], ret[1], ret[2])

# 5.3 - Cost Function
def schedulecost(sol):
    totalprice = 0
    latestarrival = 0
    earliestdep = 24 * 60

    for d in range(len(sol) / 2):
        origin = people[d][1]
        outbound = flights[(origin, destination)][int(sol[d * 2])]
        returnf  = flights[(destination, origin)][int(sol[d * 2 + 1])]
        
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

    return bestr
