import random
import csv
with open('train1.dat', 'rb') as csvfile:
	spamreader = list(csv.reader(csvfile, delimiter=',', quotechar='|'))
	random.shuffle(spamreader)
	print spamreader
