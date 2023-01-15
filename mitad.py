import math
# import numpy as np
import sys


def moveMode ( INITIAL_POSITION, POSITION, DESTINATION, twist, cmdvel_pub ):
    #startingPoint = math.sqrt(INITIAL_POSITION.x**2 + INITIAL_POSITION.y**2)
    #currentPosition = math.sqrt(POSITION.x**2 + POSITION.y**2)
    #destinationPosition = math.sqrt(DESTINATION.x**2 + DESTINATION.y**2)
    
    startingPoint = INITIAL_POSITION.x
    currentPosition = POSITION.x
    destinationPosition = DESTINATION.x


	newSpeed = inferSpeedFromDistance( startingPoint, currentPosition, destinationPosition  )

    
    twist.linear.x = newSpeed
    twist.linear.y = 0
    twist.linear.z = 0

    twist.angular.x = 0
    twist.angular.y = 0
    twist.angular.z = 0
    cmdvel_pub.publish(twist)


def inferSpeedFromDistance ( startingPoint, currentPoint, destination, maxSpeed=0.6 ):
	ratio = ( currentPoint - startingPoint ) / ( destination - startingPoint )
	return math.sin(math.pi*ratio) * maxSpeed
	
def turnToAngle ( currentAngle, destinationAngle, rate=0.5 ):
	return (destinationAngle - currentAngle) * rate
§
def addNode (node, store):
	store[f"{node[0]}:{node[1]}"] = None

def checkNode (node, store):
	return f"{node[0]}:{node[1]}" in store


"""
Going from cords to block unit -> Math.floor(value / block dimension)
"""

def pythagoras (start, end):
	return math.sqrt( (end[0]-start[0])**2  + (end[1] - start[1])**2   )

def inBucket (item, obj):
	return f"{item[0]}:{item[1]}" in obj

# Ensure the cordinates do not go out of bound
def inRange (cords, dimensions):
	return cords[0] < 0 or cords[0] >= dimensions[0] or cords[1] < 0 or cords[1] >= dimensions[1]


def runMitad (start, end, dimensions):
	
	visited = {}
	blockers = {'8:8':None}
	reserves = []
	#end = [9, 9]	
	#dimensions = [10, 10]
	#start = [0, 0]	
	path = []
	# Ensure options are valid before continuing
	def filterOptions (cords):
		if inRange(cords, dimensions):
			return False
		if inBucket(cords, visited):
			return False	
		if inBucket(cords, blockers):
			return False
		return True

	def mitad (current):
	
		if current[0] == end[0] and current[1] == end[1]:
			return True
		
		options = [
			[ current[0]-1, current[1]-1  ], # diagonal top left
			[ current[0]-1, current[1]+1  ], # diagonal top right
			[ current[0]+1, current[1]+1  ], # diagonal bottom right
			[ current[0]+1, current[1]-1  ], # diagonal bottom left
			[ current[0]-1, current[1]  ], # top
			[ current[0], current[1]+1  ], # right
			[ current[0]+1, current[1]  ], # bottom
			[ current[0], current[1]-1  ], # left
		] 

		
		options = list( filter( filterOptions, options ) )
		options_size = len(options)
		hasReserves = len(reserves) > 0
		hasOptions = options_size > 0

		if not hasOptions and hasReserves:
			options.append(reserves.pop(0))
			options_size = 1
		elif not hasOptions and not hasReserves:
			print("Complete blockade, no more options to look at")
			return False
		
		bestFitness = float('inf')
		bestNodeIndex = None
		
		# Identify which option has the best fitness using pythagoras
		for index in range(options_size):
			pythag = pythagoras(options[index], end)
			if pythag < bestFitness:
				bestFitness = pythag
				bestNodeIndex = index				
		
		# put remainder of items into the reserves for later use
		for index in range(options_size):
			if index != bestNodeIndex:
				reserves.append(options[index])
		
		visited[f"{options[bestNodeIndex][0]}:{options[bestNodeIndex][1]}"] = None		
		pathResponse = mitad(options[bestNodeIndex])
		if pathResponse:
			path.append(options[bestNodeIndex])
			return True
		return False			
	
	mitad(start)
	path.append(start)
	return path[::-1]


def identifyDirectionBetweenNodes (first, second):
	# top
	if first[1] == second[1] and (first[0] - second[0]) == 1:
		return 0
		"""
		Example:
		first    second	
		[ 9, 9 ] [ 8, 9 ]
		"""	
	# left
	if first[0] == second[0] and (first[1] - second[1]) == 1:
		return 270
		"""
		Example:
		first    second	
		[ 9, 9 ] [ 9, 8 ]
		"""	
	# bottom
	if first[1] == second[1] and (second[0] - first[0]) == 1:
		return 180
		"""
		Example:
		first    second	
		[ 8, 8 ] [ 9, 8 ]
		"""	
	# right
	if first[0] == second[0] and (second[1] - first[1]) == 1:
		return 90
		"""
		Example:
		first    second	
		[ 8, 8 ] [ 8, 9 ]
		"""

	# top left
	if (first[0] - second[0])==1 and (first[1] - second[1]) == 1:
		return 315
		"""
		Example:
		first    second	
		[ 9, 9 ] [ 8, 8 ]
		"""

	# top right
	if (first[0] - second[0])==1 and (second[1] - first[1]) == 1:
		return 45
		"""
		Example:
		first    second	
		[ 9, 9 ] [ 8, 10 ]
		"""
	
	# bottom right
	if (second[0] - first[0])==1 and (second[1] - first[1]) == 1:
		return 135
		"""
		Example:
		first    second	
		[ 9, 9 ] [ 10, 10 ]
		"""

	# bottom left
	if (second[0] - first[0])==1 and (first[1] - second[1]) == 1:
		return 225
		"""
		Example:
		first    second	
		[ 9, 9 ] [ 10, 8 ]
		"""

	return None	

"""

	1st step in path processing
	This function collapses the paths into units where the robot could move in a straight line to 
	reduce instructions at the end

"""
def generateVelocityMovement (path):
	
	# identify where you need to go top, left, right, diagonal etc
	instructions = []
	index = 1
	size = len(path) - 1
	previousDirection = identifyDirectionBetweenNodes(path[0], path[1])  
	
	"""
		t for top, l for left, r for right, b for bottom and d diagonal and d_ where _
		references what we have already mentioned above
	"""

	while index < size:
		prevInstructIndex = len(instructions) - 1
		nextDirection = identifyDirectionBetweenNodes(path[index-1], path[index])
		sameDirection = True if index==1 else nextDirection == instructions[prevInstructIndex]['direction'] 
		
		if index==1:	
			instructions.append({ 'type':'movement', 'start':path[0], 'end':None, 'direction':nextDirection  })
		
		if not sameDirection:
			instructions[ prevInstructIndex ]['end'] = path[index]
			instructions[ prevInstructIndex ]['direction'] = instructions[prevInstructIndex]['direction']	
			instructions.append({ 'type':'movement', 'start':path[index], 'end':None, 'direction':nextDirection })
				
	
		#previousDirection = nextDirection
		index += 1
	
	#print("Final instructions")
	if len(instructions):
		instructions[len(instructions)-1]['end'] = path[len(path)-1]
	#[ print(k) for k in instructions  ]

	return instructions	

"""
	Second step in processing of the path
	This will add in 'turn' features to rotate the robot when turning is necessary
"""

def identifyTurningPoints (path):
	size = len(path)
	
	if size <= 1:
		return path	

	instructions = []
	for index in range(1, size):
		previous = path[index-1]
		current = path[index]
		rotation = ((current['direction'] - previous['direction'])/360) * (2 * math.pi)
		instructions.append(previous)
		instructions.append( { 'type':'rotation', 'rotation':rotation  }  )
		instructions.append(current)
	return instructions

# Use sine rule to approximate velocities gradually over a range of time
def generateVelocities (maxSpeed=.6, unitDifference=0.01):
	summed = 0
	speeds = []
	while (summed <= 1):
		speeds.append( math.sin(math.pi*summed) * maxSpeed )
		summed += unitDifference
	return speeds	
	
# calculate height of line which corresponds to y position of node given an angle
def calculateSOH (hypotenuse, angleInDegrees):
	"""
	sin(theta) = o / h
	o = sin(theta) * h
	"""
	radiansAngle = angleInDegrees * ( math.pi / 180  )
	return math.sin(radiansAngle) * hypotenuse


# calculate width of line which corresponds to x position of node given an angle
def calculateCAH (hypotenuse, angleInDegrees):
	"""
	cos(theta) = a / h
	a = sin(theta) * h
	"""
	radiansAngle = angleInDegrees * ( math.pi / 180  )
	return math.cos(radiansAngle) * hypotenuse

if __name__ == "__main__":
	#generateVelocities()
	hyp = 20
	angle = 20
	print(" height  ", calculateSOH( hyp, angle  ))
	print(" width  ", calculateCAH( hyp, angle  ))
	
	#path = runMitad([3, 3], [9, 9], [15, 15])
	#path = generateVelocityMovement (path)		
	#path = identifyTurningPoints(path)
	#[ print(x) for x in path  ]
