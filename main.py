import sys
import numpy as np
import time
from TabuSearch import TSP
from savingVRP import saving, updateCost
from dbscan_with_pre_com import cluster


# calculateMaxCapRoadMatrix max tonage matrix for cluster
def calculateMaxCapRoadMatrix(maxCapRoadMatrix, customersList):
    newMatrix = list()
    for i in customersList:
        listMaxCapRoad = list()
        for j in customersList:
            if i == j:
                listMaxCapRoad.append(0)
            else:
                listMaxCapRoad.append(maxCapRoadMatrix[i, j])
        newMatrix.append(listMaxCapRoad)
    return np.array(newMatrix)


# Update the index corresponding to the original customer list
def updateIndexCustomer(nodes, customersList):
    customersList = np.array(customersList)
    customer = customersList[nodes]
    return customer


# costMatrix, maxCapRoadMatrix is numpy array

costMatrix = np.genfromtxt('../data/matrix_cost_260221_100.csv', delimiter=',')
maxCapRoadMatrix = np.genfromtxt('../data/matrix_maxtonage_250221.csv', delimiter=',')
demand = np.genfromtxt('../data/demand_250221.csv', delimiter=',')
vehicle = np.genfromtxt('../data/vehicle_230221.csv', delimiter=',')


startime = time.process_time()
eps = 400
minSample = 3
timeRunTabu = 10
totalCost = 0

# cost value to prohibit the vehicle from crossing an overloaded road
costRoadErr = np.max(costMatrix)*len(costMatrix)

# clustering
cluster = cluster(costMatrix, eps, minSample)
for c in cluster:

    print(c[0])
    # print(c[1])

    # max tonage matrix for each cluster
    maxCapRoadMatrixCustomers = calculateMaxCapRoadMatrix(maxCapRoadMatrix, c[0])

    # Saving
    # r, c, v = saving(costMatrix, demand, capacity, maxCapRoadMatrix, customersList)
    route, vehicle, vehicleFixCustomer = saving(c[1], demand[c[0]], vehicle, maxCapRoadMatrixCustomers, c[0])

    print(f'route: ')
    for key, value in route.items():
        value['totalD'] = demand[value['nodes']].sum()
        print(f'{" " * 8}{key}:{value}')

        # create matrix for each route
        costMatrixForRoute = updateCost(costMatrix, maxCapRoadMatrix, value['nodes'], value['Cap'], costRoadErr)

        # tabu search
        result = TSP.find_way(costMatrixForRoute, timeRunTabu)
        totalCost += result[1]

        # Update index for customers
        shortestPath = updateIndexCustomer(result[0], value['nodes'])

        print(f'{" " * 8}The shortest path: ', shortestPath)
        print(f'{" " * 8}Total cost: ', result[1])

        # If the way goes wrong then print costMatrix of route
        if result[1] >= costRoadErr:
            matrixRoadErr = costMatrixForRoute.tolist()
            print(" " * 8, matrixRoadErr)
        print(f'{" " * 8}--------------------------')

    print(f'\nThe remaining vehicles: {vehicle}\nThe remaining customers:{vehicleFixCustomer}')
    print("===========================")

print("Run time: ", time.process_time() - startime)
print("Total Cost: ", totalCost)


