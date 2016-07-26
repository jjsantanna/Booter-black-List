import storage
import datetime
import math

class Verifier:
	# accepts a vector (list) of weights
	def __init__(this):
		# get weight vector from database
		weights 		   = storage.Select('SELECT * FROM weights')
		this.weights 	   = weights[0][2:] # do not include domainName and lastUpdate column

	def UpdateScore(this, url, score):
		storage.SaveScore(url, score)

	def IsBooter(this, score):
		if score > this.threshold:
			return True
		else:
			return False

	def VectorLength(this, vector):
		length = 0.0
		for i in range(0, len(vector)):
			length += vector[i] * vector[i]
		return math.sqrt(length);

	def GetScoreVector(this, table, url):
		result = storage.Select('SELECT * FROM ' + table + ' WHERE domainName = \'' + url + '\'') 
		score_vector = []
		for score in result[0][2:]:
			score_vector.append(score)
		return score_vector

	def GetInvalidIndices(this, score_vector):
		invalid = []
		for i in range(0, len(score_vector)):
			if score_vector[i] < 0.0:
				invalid.append(i)
		# invalid.append(3) # use these statements to not use certain characteristics in the calculations
		return invalid

	def GetScaledWeightVector(this, invalids):
		max_weight = 0.0
		for i in range(0, len(this.weights)):
			if i not in invalids:
				if this.weights[i] > max_weight:
					max_weight = this.weights[i]
		scaled_weight = []
		for i in range(0, len(this.weights)):
			scaled_weight.append(this.weights[i] / max_weight)
		return scaled_weight
		# return [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0] # uncomment if you don't want to use weights

	def GetWeightedScoreVector(this, score_vector, invalids):
		# calculate new scores based on weights in range [0, max_weight]
		weighted_score_vector = list(score_vector)
		for i in range(0, len(score_vector)):
			if i not in invalids:
				weighted_score_vector[i] *= this.weights[i]
		# get maximum weight value NOT part of invalids (yes I can merge the two for loops, but this improves readability)
		max_weight = 0.0
		for i in range(0, len(score_vector)):
			if i not in invalids:
				if this.weights[i] > max_weight:
					max_weight = this.weights[i]
		# now divide each score by max_weight to re-transform it back in [0,1] range
		for i in range(0, len(weighted_score_vector)):
			weighted_score_vector[i] /= max_weight

		return weighted_score_vector				
		# return score_vector # uncomment this if you don't want to use weights

	def SaveScore(this, table, url, name, score):
		storage.SaveScore(table, url, datetime.datetime.now(), name, score)
