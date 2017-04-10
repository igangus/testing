
import sys
import unittest

import compute_averages

class TestComputeAverages(unittest.TestCase):

  def setUp(self):
    self.transactions = [
                     { 'transaction-time': '2014-10-06',
                       'merchant': 'M1', 'amount': -18800 },
                     { 'transaction-time': '2014-10-07',
                       'merchant': 'M2', 'amount': 170000 },
                     { 'transaction-time': '2014-10-08',
                       'merchant': 'Krispy Kreme Donuts', 'amount': -7000 },
                     { 'transaction-time': '2014-10-08T02:00:00.000Z',
                       'merchant': 'Credit Card Payment', 'amount': -1000 },
                     { 'transaction-time': '2014-10-08T04:00:00.000Z',
                       'merchant': 'CC Payment', 'amount': 1000 },

                     { 'transaction-time': '2014-11-02',
                       'merchant': 'M2', 'amount': -4000 },
                     { 'transaction-time': '2014-11-08',
                       'merchant': 'M3', 'amount': -7000 },
                     ]
    self.transactions_p = [
                     { 'transaction-time': '2014-11-06',
                       'merchant': 'M1', 'amount': -11000 },
                     { 'transaction-time': '2014-11-07',
                       'merchant': 'M2', 'amount': 170001 },
                     ]
    self.months = {
                     '2014-10': { 'spent': 100000, 'income': 100000 },
                     '2014-11': { 'spent': 100000, 'income': 300000 },
                   }
    compute_averages.ignore_donuts = False
    compute_averages.ignore_cc_payments = False
    compute_averages.crystal_ball = False


  def testParseData(self):
    months = compute_averages.ParseData(self.transactions, []) 
    self.assertTrue('2014-10' in months.keys())
    self.assertEqual(months['2014-10']['income'], 171000)
    self.assertEqual(months['2014-10']['spent'], 26800)
    self.assertTrue('2014-11' in months.keys())
    self.assertEqual(months['2014-11']['income'], 0)
    self.assertEqual(months['2014-11']['spent'], 11000)


  def testParseDataWithProjected(self):
    months = compute_averages.ParseData(self.transactions, self.transactions_p) 
    self.assertTrue('2014-10' in months.keys())
    self.assertEqual(months['2014-10']['income'], 171000)
    self.assertEqual(months['2014-10']['spent'], 26800)
    self.assertTrue('2014-11' in months.keys())
    self.assertEqual(months['2014-11']['income'], 170001)
    self.assertEqual(months['2014-11']['spent'], 22000)


  def testParseDataNoDonuts(self):
    compute_averages.ignore_donuts = True
    months = compute_averages.ParseData(self.transactions, []) 

    self.assertTrue('2014-10' in months.keys())
    self.assertEqual(months['2014-10']['income'], 171000)
    self.assertEqual(months['2014-10']['spent'], 19800)
    self.assertTrue('2014-11' in months.keys())
    self.assertEqual(months['2014-11']['income'], 0)
    self.assertEqual(months['2014-11']['spent'], 11000)


  def testParseDataIgnoreCC(self):
    print 'AAAAA'
    compute_averages.ignore_cc_payments = True
    months = compute_averages.ParseData(self.transactions, []) 

    self.assertTrue('2014-10' in months.keys())
    self.assertEqual(months['2014-10']['income'], 170000)
    self.assertEqual(months['2014-10']['spent'], 25800)
    self.assertTrue('2014-11' in months.keys())
    self.assertEqual(months['2014-11']['income'], 0)
    self.assertEqual(months['2014-11']['spent'], 11000)


  def testComputeAverage(self):
    compute_averages.ComputeAverageAndPrint(self.months, False)
    result = '{"2014-10": {"spent": "$10.00", "income": "$10.00"},\n' 
    result += '"2014-11": {"spent": "$10.00", "income": "$30.00"},\n' 
    result += '"average": {"spent": "$10.00", "income": "$20.00"}}' 

    self.assertEqual(sys.stdout.getvalue().strip(), result)


if __name__ == '__main__':
  unittest.main(buffer=True)
