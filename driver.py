# Developed by Ben Tobben, Summer of 2020

import pandas as ps
import time

# number of options to choose from
DIMENSIONS = 10

premiums = [0.07, 0.0575, 0.05, 0.0425, 0.04, 0.0325, 0.0375, 0.03, 0.06, 0.035]
MAX_K = [0.385, 0.508, 0.631, 0.797, 0.52, 0.714, 0.483, 0.686, 0.267, 0.443]

# A map of all combinations of -1, 0, 1 across all options.
# When searching for the max geometric mean, we change each weight for each
# option by 1, 0, or -1. OFFSET_VALUES stores all the combinations of
# these "directions"
OFFSET_VALUES = []
current_milli_time = lambda: int(round(time.time() * 1000)) # timer

# geoMean calculates and returns the geometric mean given allocations
# weights are the percentages that we are allocating to each option
# cols is an indexing list that allows us to loop through the options
# outcomes is the simulation data
def geoMean(weights, cols, outcomes):
    product = 1
    sum = 0
    cash = 1

    # calculate the unallocated cash
    for x in range(DIMENSIONS):
        cash -= weights[x]

    # iterates over each row of simulated outcomes
    for arr in outcomes:
        sum = cash
        # sums up the investment result on each simulation for all the options
        for x in range(DIMENSIONS):
            sum += arr[cols[x] + 1]*weights[x]
            # add one to the index since the count for each row is at the front

        # each simulation row occurs [arr[10]] times
        sum = sum ** arr[0]
        # multiplies the investment result of each simulation
        product *= sum
    # takes the 10000th root and subtracts 1 to get the geo mean
    return ((product ** (1/10000))-1)*100
    # Multiply by 100 for percentage
# END geoMean ##################################################################


# maxClimber starts the recursion and prints the results
# cols is an indexing list that allows us to loop through the options
# seeds is the starting allocations for the options
# outcomes is the simulation data
def maxClimber(cols, seeds, outcomes, directions):
    # the recursion returns a list of the results
    result = maxClimberAux(seeds, cols, -100, outcomes, directions)

    # parsing and printing the results
    columns = "For "
    weights = "Max mean: " + str(result[0]) + " at"
    for x in range(DIMENSIONS):
        columns += str(cols[x]+1) + ", "
        weights += ", " + str(result[1][x])

    print(columns)
    print(weights + "\n")
# END maxClimber ###############################################################


# maxClimberAux recurses until all adjacent points are less than the current
#   point. It functions similarly to a hill climber, but there is no
#   acceleration due to the variability of the function we are investigating
# weights are the current allocations to the options
# cols is an indexing list that allows us to loop through the investment options
#   being evaluated
# maxMean is the current max geometric mean that we have found
# outcomes is the simulation data
def maxClimberAux(weights, cols, maxMean:float, outcomes, directions) -> []:

    currMax = -99       # current max geometric mean
    newWeights = []     # stores weights that correspond to currMax
    newDirection = []   # stores the values for the next direction
    temp = 0.0          # just a temperary value holder
    maxTotal = 0        # the max amount of cash we can use is stored here

    # initialize newWeights
    for x in range(DIMENSIONS):
        newWeights.append(-1)

    # loop over all combinations of all directions, -1, 0, or 1, on each option
    for n in range(len(OFFSET_VALUES)):
        geoWeights = []     # a holder for the weights which will be passed
                            # to geoMean
        maxTotal = 100      # initialize to 100
        sumNewWeights = 0   # total allcated money (percentage)
        inBounds = True     # used to make sure our weights don't exceed
                            # their boundaries
        momentum = True     # keeps the climber from looking backwards, which
                            # reduces the number of calculations to perform

        # loop over the current options to prepare the values for the
        #   if statement
        for x in range(DIMENSIONS):
            if(abs(OFFSET_VALUES[n][x] - directions[x]) == 2):
                momentum = False
                break

            currWeight = weights[x] + OFFSET_VALUES[n][x]
            maxTotal += premiums[cols[x]] * currWeight # add premium to maxTotal
            # make sure that our current weights don't go over their max k value,
            # and that we don't allocate a negative percentage
            if(currWeight > (MAX_K[cols[x]])*100 or currWeight < 0):
                inBounds = False
                break;

            geoWeights.append(currWeight/100) # init geoWeights
            sumNewWeights += currWeight

        # if currWeights are at a valid position, find their geometric mean and
        # see if this point is a new max
        if(inBounds and momentum and sumNewWeights < maxTotal):
            temp = geoMean(geoWeights, cols, outcomes)
            if(temp > currMax):
                currMax = temp
                # put the current weights in newWeights
                for x in range(DIMENSIONS):
                    newWeights[x] = weights[x] + OFFSET_VALUES[n][x]

    # after looking at all the points around this one, check if we have
    # a new maxMean
    if currMax > maxMean:
        maxMean = currMax
        for x in range(DIMENSIONS):
            newDirection.append(newWeights[x] - weights[x])
        # since there is a new max mean, keep recursing
        return maxClimberAux(newWeights, cols, maxMean, outcomes, newDirection)

    # Base Case: no new max mean, return the max
    else:
        return [maxMean, newWeights]
# END maxClimberAux ############################################################


def main():
    # this is the simulation data. Each column represents an investment option,
    # and each row represents the simulated outcome of that investment in a year
    outcomes = ps.read_csv("simulation-data.csv",encoding='utf-8').to_numpy()

    curr = []           # used in making OFFSET_VALUES
    seed = []           # stores starting spot
    columns = []        # change to pick the options
    tot_max_k = 0       # used for calculating the seed
    directions = []     # the assumption is that the code won't double back,
                        # so a list of the directions chosen for each weight is
                        # maintained, and we don't look backwards

    print("Driver start")

    # init values
    for x in range(DIMENSIONS):
        curr.append(-1)
        directions.append(0)
        columns.append(x) # comment to pick the options
        tot_max_k += MAX_K[columns[x]]
        seed.append(0)

    # calculate seeds
    for x in range(DIMENSIONS):
        seed[x] = int((MAX_K[columns[x]]/tot_max_k) * 100)

    # do first iteration outside the loop to simplify the process
    if(sum(curr) > -2):
        OFFSET_VALUES.append(curr)
    #calculate OFFSET_VALUES table
    for n in range(1, 3**DIMENSIONS):
        for x in range(DIMENSIONS):
            if(n % 3**x == 0):
                curr[x] += 1
                if(curr[x] == 2):
                    curr[x] = -1

        if(sum(curr) > -2):
            OFFSET_VALUES.append(curr.copy())


    time = current_milli_time()

    maxClimber(columns, seed, outcomes, directions)

    print("Recursion time: " + str(current_milli_time() - time))

#call main
main()
