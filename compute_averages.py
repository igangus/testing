
import sys

import httplib
import json

import datetime
import getopt
import itertools

# Command line flags
ignore_donuts = False
ignore_cc_payments = False
crystal_ball = False

""" Class to encapsulate client/server communications
"""
class RemoteService:

  def __init__(self):
    self.uid = 1110590645
    self.token ='CB033D90213243D59C7CDBF704116D9B'
    self.commonArgs = '{"uid": %d, "token": "%s", "api-token": "AppTokenForInterview", "json-strict-mode": false, "json-verbose-response": false}' % (self.uid,
                                                                 self.token)

  """ Get all transaction data
  """
  def GetTransactionData(self):
    command = 'get-all-transactions'
    jsonData = '{"args": %s}' % (self.commonArgs)

    return self._ProcessRequest(command, jsonData)


  """ Get projected transaction data for a specific month
  """
  def GetProjectedData(self, year, month):
    command = 'projected-transactions-for-month'
    jsonData = '{"args": %s, "year": %d, "month": %d}' % (self.commonArgs,
                                                          year, month)
    return self._ProcessRequest(command, jsonData)
  

  """ Common code for the HTTPS request. We don't validate the certificates for
  this example.
  """ 
  def _ProcessRequest(self, command, jsonData):
    try:
      conn = httplib.HTTPSConnection('2016.api.levelmoney.com')
      conn.connect()
      request = conn.putrequest('POST', '/api/v2/core/%s' % command)
  
      headers = {}
      headers['Content-Type'] = 'application/json'
      headers['Content-Length'] = '%d' % len(jsonData)
      headers['Accept'] = 'application/json'
      headers['User-Agent'] = 'TestScript'
      for k in headers:
        conn.putheader(k, headers[k])
      conn.endheaders()
  
      conn.send(jsonData)
  
      resp = conn.getresponse()
  
      if resp.status != 200:
        raise Exception(resp.reason)
      else:
        data = resp.read()
        obj = json.JSONDecoder().decode(data)
    
        transactions = obj['transactions']
        return(transactions, None)
    except Exception, e:
      return(None, str(e))
  
    finally:
      conn.close()
  

"""
Remove - simple function only used to get a data set from a local file
rather than over the network
"""
def GetDataFromFile(fname):
  with open(fname, 'rb') as f:
    data = f.read();
    f.close()

  obj = json.JSONDecoder().decode(data)

  transactions = obj['transactions']

  return(transactions, None)


"""
Combine and filter the data. The second argument is for the projected
transactions
"""
def ParseData(transactions, transactions_p = []):
  months = {}
  cc_transactions = []
  cc_paired_transactions = []

  for t in itertools.chain(transactions, transactions_p):
    month = t['transaction-time'][:7]
    amount = t['amount']

    if ignore_donuts:
      merchant = t['merchant']
      if merchant == 'DUNKIN #336784' or merchant == 'Krispy Kreme Donuts':
        continue

    if ignore_cc_payments:
      # We assunme we can ID credit card transactions by the merchant
      merchant = t['merchant']
      if merchant == 'Credit Card Payment' or merchant == 'CC Payment':
        found_peer = False

        # Now we need to pair them up if within 24 hours
        for t2 in itertools.chain(cc_transactions):
          d1 = datetime.datetime.strptime(t['transaction-time'],
                                          '%Y-%m-%dT%H:%M:%S.%fZ')
          d2 = datetime.datetime.strptime(t2['transaction-time'],
                                          '%Y-%m-%dT%H:%M:%S.%fZ')
          td = d1 - d2
          total = amount + t2['amount']

          if abs(td.total_seconds()) <= 86400 and total == 0:
            cc_paired_transactions.append(t2)
            cc_paired_transactions.append(t)
            # We won't use the t2 iterator again so OK to use modify the list 
            cc_transactions.remove(t2)
            found_peer = True
            break

        if found_peer is False:
          cc_transactions.append(t)
        continue

    # Initialize the month's data if it doesn't exist
    if month in months:
      month_data = months[month]
    else:
      month_data = {'spent': 0, 'income': 0}
      months[month] = month_data

    if amount < 0 :
      month_data['spent'] -= amount
    else:
      month_data['income'] += amount

  # Record the detected card transactions and orphans
  if ignore_cc_payments:
    with open('credit_card_payments', 'w') as cc_file:
      cc_file.write('Paired Credit Card Transactions\n')

      for (t2, t) in zip(cc_paired_transactions[0::2],
                         cc_paired_transactions[1::2]):
        cc_file.write('%s %s %s\n' % (t2['transaction-time'],
                      t2['merchant'], t2['amount']))
        cc_file.write('%s %s %s\n\n' % (t['transaction-time'],
                      t['merchant'], t['amount']))

      # If this data set has any unpaired transactions issue a warning 
      if cc_transactions:
        sys.stderr.write('Warning: Orphan Credit Card transactions detected\n')

      # Record the observed orphans 
      cc_file.write('Orphan Credit Card Entries\n')
      for t in itertools.chain(cc_transactions):
        cc_file.write('%s %s %s\n' % (t['transaction-time'], t['merchant'],
                      t['amount']))

  return months

"""
Compute the average income and expenditures over a month and print the results.
In general we do not include the current month as we are most likely only part
way through.
"""
def ComputeAverageAndPrint(months, include_partial_last_month = False):
  n_months = 0
  s_income = 0.0
  s_spent = 0.0

  if not include_partial_last_month:
    now = datetime.date.today()
    lastMonth = '%d-%02d' % (now.year, now.month)

  sys.stdout.write('{')

  for m in sorted(months.keys()):
    income = float(months[m]['income']) / 10000
    spent = float(months[m]['spent']) / 10000 

    print '"%s": {"spent": "$%0.2f", "income": "$%0.2f"},' % (m, spent, income) 

    if not include_partial_last_month and m == lastMonth:
      # print 'Excluding %s %d' % (m,  n_months)
      continue

    s_income += income
    s_spent += spent
    n_months += 1

  sys.stdout.write('"average": {"spent": "$%0.2f", "income": "$%0.2f"}'
                      % (s_spent/n_months, s_income/n_months)) 

  sys.stdout.write('}\n')


def PrintUsage():
  print 'Usage: python compute_averages.py [args] where arguments can be\n' \
        '--help : print out available options and exit\n' \
        '--ignore-donuts : Ignore all expenditures on donuts\n'\
        '--ignore-cc-payments : Exclude credit card payment transactions. ' \
        'A listing of the transactions will be writen to the file ' \
        '\'credit_card_payments\'\n' \
        '--crystal-ball " Include a projection for the last month\n'


if __name__ == "__main__":
  try:
    (opts, args) = getopt.getopt(sys.argv[1:], "", ['ignore-donuts',
                         'ignore-cc-payments', 'crystal-ball', 'help'])
  except getopt.GetoptError:
    print "Invalid argument"
    PrintUsage()
    sys.exit(2)

  for opt, arg in opts:
    if opt == "--ignore-donuts":
      ignore_donuts = True
    elif opt == "--ignore-cc-payments":
      ignore_cc_payments = True
    elif opt == "--crystal-ball":
      crystal_ball = True
    elif opt == "--help":
      PrintUsage()
      sys.exit(0)
    else:
      assert False, 'Unhandled option: %s' % opt

  service = RemoteService()

  (transactions, error) = service.GetTransactionData()
  # (transactions, error) = GetDataFromFile('all_transactions')

  if error is not None:
    print 'Error retrieving transactions: %s' % str(error)
    sys.exit(1)

  if crystal_ball:
    now = datetime.date.today()
    (transactions_p, error) = service.GetProjectedData(now.year, now.month)
    # (transactions_p, error) = GetDataFromFile('projected_transactions')
    if error is not None:
      print 'Error retrieving projected transactions: %s' % str(error)
      sys.exit(1)
  else:
    transactions_p = []

  months = ParseData(transactions, transactions_p)
  ComputeAverageAndPrint(months, crystal_ball)

