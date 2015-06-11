from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import csv, time

API_KEY = 'XXXXXXXXXXXX'

CLIENT_SECRET = 'client_secret.json'
SCOPES = [
		'https://www.googleapis.com/auth/prediction',
		'https://www.googleapis.com/auth/devstorage.read_only'
	]

# open test file and set up credentials
csvfile = open('fixed_adult.test')
rdr = csv.reader(csvfile)
store = file.Storage('storage.json')
flags = tools.argparser.parse_args(args=[])
credentials = store.get()
if not credentials or credentials.invalid:
	flow = client.flow_from_clientsecrets(CLIENT_SECRET, SCOPES)
	credentials = tools.run_flow(flow, store, flags)

# because it is expected that there are significantly less people who make more 
# than 50K a year, set up counters for how many times the prediction is 
# is incorrect for both classes to examine the effects of this fact
num_more_incorrect = 0
num_less_incorrect = 0
num_total = 0
num_more = 0

# begin prediction phase
service = build('prediction','v1.6', http=credentials.authorize(Http()))
print 'running'
for temp in rdr:
	# not sure exactly what the Google Prediction rate limits are, 
	# but it seems only several hundred examples can be classified before
	# they are exceeded, thus the try/except statement forcing the time delay
	try:
		x = service.trainedmodels().predict(project='81739751424', 
									id='datarobottakehomeproject', 
									body={"input":
										 {"csvInstance":temp[1:]}}).execute()
		# print temp[0], x['outputLabel']
		if temp[0] == 'more':
			num_more += 1
			if x['outputLabel'] != temp[0]:
				num_more_incorrect += 1
		else:
			if x['outputLabel'] != temp[0]:
				num_less_incorrect += 1
		num_total += 1
		print num_total

	except:
		print 'waiting'
		time.sleep(600)
		print 'running'

num_incorrect = num_less_incorrect + num_more_incorrect
print '# examples "more" : ', num_more, '\ttotal # examples : ', num_total
print '# incorrect more : ', num_more_incorrect, '\t# incorrect less : ', num_less_incorrect
print 'percent accuracy : s', float(num_incorrect)/float(num_total)