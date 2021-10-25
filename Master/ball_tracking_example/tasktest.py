#start define subtasks

nums = list(range(100))

def task_1(nums=nums):
	num = nums.pop()

	return True, num

def task_2(num):

	return True, num + 1

def task_3(num):

	return True, num + 1

def task_4(num):

	return True, num + 1

def task_5(num1, num2):

	print(num1+num2)

	return True, None


# Export functions as tasks
tasks = [
    task_1,
    task_2,
    task_3,
    task_4,
    task_5,
]
