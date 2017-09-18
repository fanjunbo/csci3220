from sys import argv
import copy

class Path:
	def __init__(self):
		self.path = []
		self.terminated = False

	def __init__(self, currentPosition):
		self.path = [currentPosition]
		self.terminated = False

	def next(self, nextPosition):
		self.path.append(nextPosition)
		return self

	def setTerminated(self):
		self.terminated = True

	def isTerminated(self):
		return self.terminated



class LocalAlignmentMatcher:
	def __init__(self, fstSeq, secSeq):
		self.fstSeq, self.secSeq = fstSeq, secSeq
		self.matchScore = self.mismatchScore = self.indelScore = 0

	def setMatchScore(self, matchScore):
		self.matchScore = matchScore

	def setMismatchScore(self, mismatchScore):
		self.mismatchScore = mismatchScore

	def setIndelScore(self, indelScore):
		self.indelScore = indelScore

	def initScoreTable(self, rowLength, colLength):
		self.table = [[0 for i in range(colLength + 1)] for j in range(rowLength + 1)]

	def getMaxValue(self, matrix):
		currentMax = matrix[0][0]
		for i in range(len(matrix)):
			for j in range(len(matrix[i])):
				if currentMax < matrix[i][j]:
					currentMax = matrix[i][j]
		return currentMax

	def hasUnfinishedPath(self, paths):
		unfinishedPath = False
		for path in paths:
			if not path.isTerminated():
				unfinishedPath = True
				return unfinishedPath
		return unfinishedPath

	def positionHasIncomeArrows(self, position):
		if position[0] == len(self.table) - 1 or position[1] == len(self.table[0]) - 1:
			return False
		else:
			diagonalMatchScore = self.mismatchScore
			if self.fstSeq[position[0]] == self.secSeq[position[1]]:
				diagonalMatchScore = self.matchScore
			if self.table[position[0] + 1][position[1] + 1] + diagonalMatchScore == self.table[position[0]][position[1]]:
				return True
			elif self.table[position[0] + 1][position[1]] + self.indelScore == self.table[position[0]][position[1]]:
				return True
			elif self.table[position[0]][position[1] + 1] + self.indelScore == self.table[position[0]][position[1]]:
				return True
			else:
				return False

	def getNextStepInfoOfPath(self, currentPath):
		position = currentPath.path[-1]
		res = []
		diagonalMatchScore = self.mismatchScore
		if self.fstSeq[position[0]] == self.secSeq[position[1]]:
			diagonalMatchScore = self.matchScore
		if self.table[position[0] + 1][position[1] + 1] + diagonalMatchScore == self.table[position[0]][position[1]]:
			if self.positionHasIncomeArrows([position[0] + 1, position[1] + 1]):
				res.append([position[0] + 1, position[1] + 1])
		if self.table[position[0] + 1][position[1]] + self.indelScore == self.table[position[0]][position[1]]:
			if self.positionHasIncomeArrows([position[0] + 1, position[1]]):
				res.append([position[0] + 1, position[1]])
		if self.table[position[0]][position[1] + 1] + self.indelScore == self.table[position[0]][position[1]]:
			if self.positionHasIncomeArrows([position[0], position[1] + 1]):
				res.append([position[0], position[1] + 1])
		return res

	def isOutputPath(self, currentPath):
		position = currentPath.path[-1]
		diagonalMatchScore = self.mismatchScore
		if self.fstSeq[position[0]] == self.secSeq[position[1]]:
			diagonalMatchScore = self.matchScore
		if self.table[position[0] + 1][position[1] + 1] + diagonalMatchScore == self.table[position[0]][position[1]] and self.table[position[0] + 1][position[1] + 1] == 0:
			return True
		if self.table[position[0] + 1][position[1]] + self.indelScore == self.table[position[0]][position[1]] and self.table[position[0] + 1][position[1]] == 0:
			return True
		if self.table[position[0]][position[1] + 1] + self.indelScore == self.table[position[0]][position[1]] and self.table[position[0]][position[1] + 1] == 0:
			return True
		return False


	def convertPathToReadable(self, path):
		fstPath, secPath = '', ''
		for i in range(1, len(path.path)):
			currentPoint, prevPoint = path.path[i], path.path[i - 1]
			if currentPoint[0] == prevPoint[0] + 1 and currentPoint[1] == prevPoint[1] + 1:
				fstPath += self.fstSeq[prevPoint[0]]
				secPath += self.secSeq[prevPoint[1]]
			elif currentPoint[0] == prevPoint[0] + 1:
				fstPath += self.fstSeq[prevPoint[0]]
				secPath += '_'
			else:
				fstPath += '_'
				secPath += self.secSeq[prevPoint[1]]
		fstPath += self.fstSeq[path.path[-1][0]]
		secPath += self.secSeq[path.path[-1][1]]
	
		fstPath = str(path.path[0][0] + 1) + ' ' + fstPath + ' ' + str(path.path[-1][0] + 1)
		secPath = str(path.path[0][1] + 1) + ' ' + secPath + ' ' + str(path.path[-1][1] + 1)
		return [fstPath, secPath]


	def convertPathsToReadable(self, paths):
		return [self.convertPathToReadable(path) for path in paths]

	def run(self):
		rowLength, colLength = len(self.fstSeq), len(self.secSeq)
		self.initScoreTable(rowLength, colLength)
		rowIndex, colIndex = rowLength - 1, colLength - 1
		for col in range(colIndex, -1, -1):
			for row in range(rowIndex, -1, -1):
				if self.fstSeq[row] == self.secSeq[col]:
					self.table[row][col] = max(0, self.table[row+1][col+1] + self.matchScore, self.table[row+1][col] + self.indelScore, self.table[row][col+1] + self.indelScore)
				else:
					self.table[row][col] = max(0, self.table[row+1][col+1] + self.mismatchScore, self.table[row+1][col] + self.indelScore, self.table[row][col+1] + self.indelScore)
		for i in range(len(self.table)):
			print self.table[i]

		maxAlignmentScore = self.getMaxValue(self.table)
		allPaths = []
		for row in range(len(self.table) - 1):
			for col in range(len(self.table[row]) - 1):
				if self.table[row][col] < maxAlignmentScore:
					continue
				allPaths.append(Path([row, col]))

		finishedPaths = []
		while len(allPaths):
			fstPath, allPaths = allPaths[0], allPaths[1:]
			res = self.getNextStepInfoOfPath(fstPath)
			if self.isOutputPath(fstPath):
				finishedPaths.append(copy.deepcopy(fstPath))
			for position in res:
				tempPath = copy.deepcopy(fstPath)
				allPaths.append(tempPath.next(position))
		for path in finishedPaths:
			print path.path
		readablePaths = self.convertPathsToReadable(finishedPaths)

		print maxAlignmentScore
		print '' 
		for readablePath in readablePaths:
			print readablePath[0]
			print readablePath[1]
			print ''

		

if __name__ == '__main__':
	fstSeq, secSeq, matchScore, mismatchScore, indelScore = argv[1:]
	matchScore, mismatchScore, indelScore = int(matchScore), int(mismatchScore), int(indelScore)

	matcher = LocalAlignmentMatcher(fstSeq, secSeq)
	matcher.setMatchScore(matchScore)
	matcher.setMismatchScore(mismatchScore)
	matcher.setIndelScore(indelScore)

	matcher.run()