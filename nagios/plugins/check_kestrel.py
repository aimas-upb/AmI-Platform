def usage():
	print "\n"
	print "==================="
	print "=check_kestrel.py:="
	print "==================="
	print "Checks the connectivity to a kestrel server and retreives data regarding server or queue status"
	print "Mandatory parameters: None"
	print "Optional parameters:"
	print "\t -h --help : displays this text"
	print "\t -H --hostname [server_ip] : specifies the server's IP address. Default is localhost."
	print "\t -p --port [port_number] : specifies the server's port. Default is 22133."
	print "\t -q --queue [queue_name] : specifies the queue that must be checked. Default is server, retrieving global server data."
	print "\n"
	print "Author: Lacea Dragos Alin, Polytechnic University of Bucharest"
	print "27.02.2013"
	
if __name__ == '__main__':
	import kestrel
	import getopt, sys
	
	kHost = 'localhost'
	kPort = '22133'
	kQueue = ''
	
	try:
		options, args = getopt.getopt(sys.argv[1:],"hH:p:q:", ["help", "hostname=", "port=", "queue="])
	except getopt.GetoptError:
		printUsage()
		sys.exit(3)
	for name, value in options:
		if name in ("-h", "--help"):
			usage()
			sys.exit(0)
		if name in ("-H", "--hostname"):
			kHost = value
		if name in ("-p", "--port"):
			kPort = value
		if name in ("-q", "--queue"):
			kQueue = value
	
	try:
		conn = kestrel.Client([kHost + ":" + kPort])
	except Exception:
		print 'Kestrel server unreachable!'
		sys.exit(3)
	try:
		stats = conn.stats()[1]
		if kQueue == '':
			s = stats["server"]
		else:
			s = stats["queues"][kQueue]
		
		print "Current items = " + str(s["items"]) + " Current size: " +str(s["bytes"])		
		sys.exit(0)
	except Exception:
		print sys.exc_info()[0]
		sys.exit(2)