#!/usr/bin/python3

import sys
import datetime

accounts = dict()
categories = dict()
history = list()
read_header = True

def ASSERT(condition, msg):
	if not condition:
		print("ERROR: ASSERTION FAILED:", msg)
		exit(1)


with open("budget_db", "r") as file:
	current = None
	for line in file:
		if len(line) < 2 or " " == line[0] or "#" == line[0]:
			continue
		if read_header:
			if "A" == line[0]:
				temp = line.split(" ", 2)
				accounts[temp[0]] = int(temp[1])
			elif "C" == line[0]:
				current = line[:-1].split(" ", 1)[0]
				categories[current] = set()
			elif "S" == line[0]:
				ASSERT(current is not None, "current is not None")
				categories[current].add(line[:-1].split(" ", 1)[0])
			elif "H" == line[0]:
				read_header = False
		else:
			temp = line[:-1].split(" ", 5)
			data = int(temp[0])
			amount = int(temp[1])
			inout = temp[2] == "in"
			ASSERT(temp[3] in accounts, "temp[3] in accounts")
			account = temp[3]
			ASSERT(temp[4] in categories, "temp[4] in categories")
			category = temp[4]
			subcategory = ""
			comment = ""
			if len(temp) == 6:
				temp = temp[5]
				if temp[0] == "S":
					temp = temp.split(" ", 1)
					ASSERT(temp[0] in categories[category], "temp[0] in categories[category]")
					subcategory = temp[0]
					if len(temp) == 2:
						comment = temp[1].lstrip()
				else:
					comment = temp.strip()
			history.append({"data": data, "amount": amount, "inout": inout, "account": account, "category": category, "subcategory": subcategory, "comment": comment})
ASSERT(not read_header, "not read_header")
#print(accounts)
#print(categories)
#print(history)
#print(sys.argv)

if len(sys.argv) == 1:
	exit()
ASSERT(len(sys.argv) >= 2, "len(sys.argv) >= 2")

#budget new_account account
if sys.argv[1] == "new_account":
	ASSERT(len(sys.argv) == 3, "len(sys.argv) = 3")
	account = "A_" + sys.argv[2]
	ASSERT(account not in accounts, "This account already exist, dumbass :p")
	accounts[account] = 0

#budget new_category category
elif sys.argv[1] == "new_category":
	ASSERT(len(sys.argv) == 3, "len(sys.argv) == 3")
	category = "C_" + sys.argv[2]
	ASSERT(category not in categories, "This category already exist, dumbass :p")
	categories[category] = set()

#budget new_subcategory subcategory in category
elif sys.argv[1] == "new_subcategory":
	ASSERT(len(sys.argv) == 5, "len(sys.argv) == 5")
	subcategory = "S_" + sys.argv[2]
	category = "C_" + sys.argv[4]
	ASSERT(sys.argv[3] == "in", "sys.argv[3] == 'in'")
	ASSERT(category in categories, "category in categories")
	ASSERT(subcategory not in categories[category], "This subcategory already exist, dumbass :p")
	categories[category].add(subcategory)

#budget (in|out) account amount category [subcategory] [# comment] #income|outcome

elif sys.argv[1] in ("in", "out"):
	ASSERT(len(sys.argv) in range(5,8), "len(sys.argv) in range(5,8)")
	inout = sys.argv[1] == "in"
	account = "A_" + sys.argv[2]
	ASSERT(account in accounts, "Sorry, this account doesn't exist, idiot :P")
	category = "C_" + sys.argv[4]
	ASSERT(category in categories, "Sorry, this category doesn't exist, idiot :P")
	subcategory = ""
	comment = ""
	if len(sys.argv) == 5:
		pass
	elif len(sys.argv) == 6:
		if sys.argv[5][0] == "#":
			comment = sys.argv[5]
		else:
			subcategory = "S_" + sys.argv[5]
			ASSERT(subcategory in categories[category], "subcategory in categories[category]")
	else:
		subcategory = "S_" + sys.argv[5]
		ASSERT(subcategory not in categories[category], "subcategory not in categories[category]")
		comment = sys.argv[6]
	accounts[account] += (1 if inout else -1) * amount
	date = datetime.datetime.now()
	date = date.year * 10000 + date.month * 100 + date.day
	history.append({"data": date, "inout": inout, "account": account, "amount": amount, "category": category, "subcategory": subcategory, "comment": comment})

#budget transfer amount from account_1 to account_2 [# comment]

elif sys.argv[1] == "transfer":
	ASSERT(len(sys.argv) in range(7,9), "len(sys.argv) in range(7,9)")
	ASSERT(sys.argv[3] == "from", "sys.argv[3] == 'from'")
	ASSERT(sys.argv[5] == "to", "sys.argv[5] == 'to'")
	amount = int(sys.argv[2])
	account_1 = "A_" + sys.argv[4]
	account_2 = "A_" + sys.argv[6]
	ASSERT(account_1 in accounts, "Sorry, this account doesn't exist, stupid")
	ASSERT(account_2 in accounts, "Sorry, this account doesn't exist, stupid")
	comment = ""
	if len(sys.argv) == 7:
		pass
	elif len(sys.argv) == 8:
		ASSERT(sys.argv[7][0] == "#", "sys.argv[7][0] == '#'")
		comment = sys.argv[7]
	accounts[account_1] += -amount
	accounts[account_2] += amount
	date = datetime.datetime.now()
	date = date.year * 10000 + date.month * 100 + date.day
	history.append({"data": date, "inout": False, "account": account_1, "amount": amount, "category": "C_transfer", "subcategory": "", "comment": comment})
	history.append({"data": date, "inout": True,  "account": account_2, "amount": amount, "category": "C_transfer", "subcategory": "", "comment": comment})

#budget summary

elif sys.argv[1] == "summary":
	ASSERT(len(sys.argv) == 2, "len(sys.argv) == 2")
	sum = 0
	for account in accounts:
		sum += abs(accounts[account])
	for account in accounts:
		accounts[account]/sum
		print(f"{accounts[account]/100}zl {account[2:]} {round(accounts[account]/sum * 100, 2)}%")


#budget history number

elif sys.argv[1] == "history":
	ASSERT(len(sys.argv) == 3, "len(sys.argv) == 3")
	number = int(sys.argv[2])
	for element in reversed(history[-number:]):
		data = element['data']
		day = data % 100
		month = (data % 10000) // 100
		year = data // 10000
		month = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"][month - 1]
		data = f"{day} {month} {year}"
		amount = f"\x1b[{'38;5;10m+' if element['inout'] else '38;5;9m-'}{element['amount']}\x1b[0m"
		print(f"{data} {element['account'][2:]} {amount} {element['category'][2:]} {element['subcategory'][2:]} {element['comment']}")


with open("budget_db", "w") as file:
	for account in accounts:
		file.write(f"{account} {accounts[account]}\n")
	for category in categories:
		file.write(f"{category}\n")
		for subcategory in categories[category]:
			file.write(f"{subcategory}\n")
	file.write("H\n")
	for element in history:
		file.write(f"{element['data']} {element['amount']} {'in' if element['inout'] else 'out'} {element['account']} {element['category']} {element['subcategory']} {element['comment']}\n")
