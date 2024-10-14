import csv
import time
from itertools import combinations
from efficient_apriori import apriori # type: ignore
from fpgrowth_py import fpgrowth # type: ignore

"""
dict {
    'count': int,
    'keyset': set,
    'support': int
}
"""
# Dictionary of Itemset Options
def getDataset(option):
    nameMap = {
        '1': ('amazonitems.csv', 'amazontransactions.csv'),
        '2': ('bestbuyitems.csv', 'bestbuytransactions.csv'),
        '3': ('kmartitems.csv', 'kmarttransactions.csv'),
        '4': ('nikeitems.csv', 'niketransactions.csv'),
        '5': ('genericitems.csv', 'generictransactions.csv')
    }
    return nameMap[option]

def myApriori(items: set, transactions, previtemset=None, returnSet = {}):
    # generate itemsets
    itemset = {}
    if previtemset == None:     # k = 1
        for item in items:
            itemset[item] = {}
            itemset[item]['count'] = 0
            itemset[item]['keyset'] = {item}
    else:   # k > 1
        for key in previtemset:
            for item in items:
                if item not in previtemset[key]['keyset']:
                    tempkeyset = previtemset[key]['keyset'].copy()
                    tempkeyset.add(item)
                    newKey = ''.join(sorted(tempkeyset))
                    if newKey not in itemset:
                        itemset[newKey] = {}
                        itemset[newKey]['count'] = 0
                        itemset[newKey]['keyset'] = tempkeyset

    # gets frequencies of itemsets
    for key in itemset:
        for transaction in transactions:
            exists = True
            for item in itemset[key]['keyset']:
                if item not in transaction:
                    exists = False
                    break
            if exists:
                itemset[key]['count'] += 1

    # removes nonfrequent items
    keys = list(itemset.keys())
    for key in keys:
        itemSupport = itemset[key]['count'] / len(transactions)
        if itemSupport < support:
            del itemset[key]
        else:
            itemset[key]['support'] = itemSupport
    
    # recursion for k + 1
    if len(itemset.keys()) > 0:
        for key in itemset:
            frequentitemsets.append([itemset[key]['keyset'], itemset[key]['count']])
        returnSet.update(itemset)
        return myApriori(items, transactions, previtemset=itemset, returnSet=returnSet)
    else:
        return returnSet

def efficientApriori(transactions, support, confidence):
    return apriori(transactions=transactions, min_support=support, min_confidence=confidence)

def fpGrowth(transactions, support, confidence):
    return fpgrowth(transactions, support, confidence)

def generateAssociationRules(frequentItemSets, support, confidence, itemsetData):
    rules = []
    for key in itemsetData:
        items = list(itemsetData[key]['keyset'])
        itemsetSupport = itemsetData[key]['support']
        print(items)
        if len(items) > 1:
            for i in range(1, len(items)):
                for antecedent in combinations(items, i):
                    antecedent = frozenset(antecedent)
                    consequent = frozenset(items) - antecedent
                    antecedentKey = ''.join(sorted(antecedent))
                    antecedentSupport = itemsetData[antecedentKey]['support']
                    if antecedentSupport > 0:
                        ruleConfidence = itemsetSupport / antecedentSupport
                        if ruleConfidence >= confidence:
                            rules.append({
                                'antecedent': antecedent,
                                'consequent': consequent,
                                'support': itemsetSupport,
                                'confidence': ruleConfidence
                            })
    return rules
                

# _____________________________________MAIN_____________________________________
frequentitemsets = []
dataset = input("Select a Dataset: ")
support = float(input("Enter a minimum support(must be in decimal format Ex. 0.5, 0.7): "))
confidence = float(input("Enter a minimum confidence(must be in decimal format Ex. 0.5, 0.7): "))

items, transactions = getDataset(dataset)
itemset = set()
transactionList = []
eaTransactionList = []

# preproccessing of data
# reads CSV files and converts to lists
with open(items, 'r', encoding='utf-8-sig') as csvFile:
    itemListReader = csv.reader(csvFile)
    for row in itemListReader:
        itemset.add(row[0])

with open(transactions, 'r', encoding='utf-8-sig') as csvFile:
    transactionListReader = csv.reader(csvFile)
    for row in transactionListReader:
        transactionList.append(row)
        eaTransactionList.append(tuple(row))

print('selected dataset transactions:', transactionList)

myAprioriStart = time.time()
itemsetData=myApriori(itemset, transactionList)
rules = generateAssociationRules(frequentitemsets, support, confidence, itemsetData)
myAprioriEnd = time.time()
# for itemSet, count in frequentitemsets:
#     print('ItemSet:', itemSet, ':', count)


efficientAprioriStart = time.time()
itemset1, rules1 = efficientApriori(eaTransactionList, support, confidence)
efficientAprioriEnd = time.time()


fpGrowthStart = time.time()
rules2 = fpGrowth(transactionList, support, confidence)
fpGrowthEnd = time.time()
display = input('Would you like to print results(y/n)?')
print('(algorithm performances will print regardless)')
if display == 'y':
    print("\nmy apriori solution:")
    for rule in rules:
        print(f"Rule: {set(rule['antecedent'])} -> {set(rule['consequent'])}")
        print(f"Support: {rule['support']:.2f}, Confidence: {rule['confidence']:.2f}")

    print("efficient_apriori solution:")
    print(rules1)
    print("fpgrowth_py solution:")
    print(rules2)

print("\nAlgorithm Performances")
print("----------------------")
print("My Apriori:", myAprioriEnd - myAprioriStart)
print("Efficient Apriori:", efficientAprioriEnd - efficientAprioriStart)
print("FPGrowth:", fpGrowthEnd - fpGrowthStart)