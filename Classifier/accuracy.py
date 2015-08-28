import datetime
import storage



metrics = ['euclidean' , 'squared_euclidean', 'manhattan', 'cosine', 'fractional', 'naive_bayes', 'knn']

test_table_to_verification = {}
test_table_to_verification['scores']  = 'verification'
test_table_to_verification['test_scores']  = 'verification'
test_table_to_verification['test_scores2'] = 'verification2'
test_table_to_verification['test_scores3'] = 'verification3'

def CalculateAccuracy(thresholds):
	# obtain score results from multiple test datasets
	# test_tables = ['test_scores', 'test_scores2', 'test_scores3']
	test_tables = ['scores']
	test_scores = {}
	for table in test_tables:
		# select a pseudo-random list of scores to test on the entire database
		query  = 'SELECT urls.domainName, urls.[booter?] FROM ' + table + ' '
		query += 'INNER JOIN urls ON urls.domainName = ' + table + '.domainName '
		query += 'WHERE urls.[booter?] != \'?\' AND urls.status = \'on\''
		# query += 'LIMIT 465'
		test_scores[table] = storage.Select(query)

	# for each test_score dataset, calculate the accuracy metrics
	test_results = {}
	for test_table in test_scores:
		test_results[test_table] =  {}
		true_positives  = {} # key = metric, value = list of urls
		true_negatives  = {}
		false_positives = {}
		false_negatives = {}
		# first initialize empty lists on each of the confusion metrics
		for metric in metrics:
			test_results[test_table][metric] = {}
			true_positives[metric]  = []
			true_negatives[metric]  = []
			false_positives[metric] = []
			false_negatives[metric] = []
		# then test for accuracy
		for test_url in test_scores[test_table]:
			url       = test_url[0]
			is_booter = True if test_url[1] == 'Y' else False
			scores    = storage.Select('SELECT * FROM ' + test_table_to_verification[test_table] + ' WHERE domainName = \'' + url + '\'')[0][2:] 
			for i in range(0, len(scores)):
				metric    = metrics[i]
				score     = scores[i]
				threshold = thresholds[i]
				if   score >= threshold and     is_booter:
					true_positives[metric].append(url)
				elif score >= threshold and not is_booter:
					false_positives[metric].append(url)
				elif score <  threshold and not is_booter:
					true_negatives[metric].append(url)
				elif score <  threshold and     is_booter:
					false_negatives[metric].append(url)
		# then store results
		for metric in metrics:
			test_results[test_table][metric] = { 
				"tp" : true_positives[metric], 
				"tn" : true_negatives[metric], 
				"fp" : false_positives[metric], 
				"fn" : false_negatives[metric] 
			}

	# now average results and return final accuracy scores
	final_results = {}
	for metric in metrics:
		final_results[metric] = {}
		final_results[metric]["tp"] = 0
		final_results[metric]["tn"] = 0
		final_results[metric]["fp"] = 0
		final_results[metric]["fn"] = 0
	for test_table in test_results:
		for metric in metrics:
			true_positives  = test_results[test_table][metric]["tp"]
			true_negatives  = test_results[test_table][metric]["tn"]
			false_positives = test_results[test_table][metric]["fp"]
			false_negatives = test_results[test_table][metric]["fn"]
			final_results[metric]["tp"] += len(true_positives)
			final_results[metric]["tn"] += len(true_negatives)
			final_results[metric]["fp"] += len(false_positives)
			final_results[metric]["fn"] += len(false_negatives)
	for metric in metrics:
		final_results[metric]["tp"] /= len(test_tables)
		final_results[metric]["tn"] /= len(test_tables)
		final_results[metric]["fp"] /= len(test_tables)
		final_results[metric]["fn"] /= len(test_tables)

	return final_results 
 
def PrintResults(results, exclude_fn, print_to_file, metricz = '', k = 0):
	if print_to_file:
		filez = open("accuracy_output.txt", "a")
		filez.write('-----------------------------\n')
		filez.write(' ' + metricz + '      K = ' + str(k) + ' \n')
		filez.write('-----------------------------\n')
	for metric in metrics:
		print('== ==================')
		print(metric)
		print('== ==================')
		nr_true_positives  = results[metric]['tp']
		nr_true_negatives  = results[metric]['tn']
		nr_false_positives = results[metric]['fp']
		nr_false_negatives = results[metric]['fn']
		if exclude_fn:
			nr_false_negatives = 0 # if we don't care about false negatives, what will our accuracy then be?
		nr_total		   = nr_true_positives + nr_true_negatives + nr_false_positives + nr_false_negatives
		accuracy           = (nr_true_positives + nr_true_negatives) / nr_total
		print('#true_positives : ' + str(nr_true_positives))
		print('#true_negatives : ' + str(nr_true_negatives))
		print('#false_positives: ' + str(nr_false_positives))
		if not exclude_fn:
			print('#false_negatives: ' + str(nr_false_negatives)) 
		print('-- ------------------')
		print('accuracy: ' + str(accuracy * 100.0) + '%')
		print()
		if print_to_file:
			filez.write('== ==================\n')
			filez.write(metric + '\n')
			filez.write('== ==================\n')
			filez.write('#true_positives : ' + str(nr_true_positives) + '\n')
			filez.write('#true_negatives : ' + str(nr_true_negatives) + '\n')
			filez.write('#false_positives: ' + str(nr_false_positives) + '\n')
			if not exclude_fn:
				filez.write('#false_negatives: ' + str(nr_false_negatives) + '\n') 
			filez.write('-- ------------------\n')
			filez.write('accuracy: ' + str(accuracy * 100.0) + '% \n')
			filez.write('\n')




# calculates `increments` amount of accuracy scores where each increment is one
# threshold value T. Returns a list of a selected table of scores to find the
# optimal threshold (note: this should only be executed on training data); the
# subsequent accuracy tests should use this 'trained' threshold for their 
# measurements.
def CalculateThresholds(increments, metric, score_table):
	# select a pseudo-random list of scores to test on the entire database
	query  = 'SELECT urls.domainName, urls.[booter?] FROM ' + score_table + ' '
	query += 'INNER JOIN urls ON urls.domainName = ' + score_table + '.domainName '
	query += 'WHERE urls.[booter?] != \'?\' AND urls.status = \'on\''
	test_urls = storage.Select(query) 
	results = {}
	for i in range(0, increments + 1):
		threshold = i / increments
		# first initialize empty lists on each of the confusion metrics
		true_positives  = []
		true_negatives  = []
		false_positives = []
		false_negatives = []
		# then test for accuracy
		for test_url in test_urls:
			url       = test_url[0]
			is_booter = True if test_url[1] == 'Y' else False
			score     = storage.Select('SELECT ' + metric + ' FROM ' + test_table_to_verification[score_table] + ' WHERE domainName = \'' + url + '\'')[0][0] 
			if   score >= threshold and     is_booter:
				true_positives.append(url)
			elif score >= threshold and not is_booter:
				false_positives.append(url)
			elif score <  threshold and not is_booter:
				true_negatives.append(url)
			elif score <  threshold and     is_booter:
				false_negatives.append(url)
		results[i] = { "tp" : true_positives, "fp" : false_positives, "tn" : true_negatives, "fn" : false_negatives }

	return results


def PrintThresholds(thresholds, gnu_file = 'gnu/accuracy.dat'):
	f = open(gnu_file, 'w')
	f.write('Threshold,\tAccuracy Rate,\t\tType I Error,\t\tType II Error\n')
	print('== ==================')
	for i in range(0, len(thresholds)): 
		threshold       = i / (len(thresholds) - 1)
		true_positives  = thresholds[i]['tp']
		true_negatives  = thresholds[i]['tn']
		false_positives = thresholds[i]['fp']
		false_negatives = thresholds[i]['fn']

		nr_total = len(true_positives) + len(true_negatives) + len(false_positives) + len(false_negatives)
		CAR      = (len(true_positives) + len(true_negatives)) / nr_total
		TI_er    = len(false_positives) / nr_total
		TII_er   = len(false_negatives) / nr_total
		print('Threshold: ' + str(threshold) + '\t||| ' + 'CAR: ' + "{0:.5f}".format(CAR) + '   | TI_er: ' + "{0:.5f}".format(TI_er) + '   | TII_er: ' + "{0:.5f}".format(TII_er))		
		# also store in file
		f.write(str(threshold) + ',\t\t' + str(CAR) + ',\t' + str(TI_er) + ',\t' + str(TII_er) + '\n')		
	f.close()
	print('== ==================')