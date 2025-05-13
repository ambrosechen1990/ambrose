import random
import string


#邮箱名称和密码
email = "13402612115@gmail.com"
password = "Aa12345678"

#随机数
ran1 = ''.join(random.choice(string.ascii_letters) for _ in range(8))
# 生成一个由随机字母组成的字符串，长度为20
ran2 = ''.join(random.choice(string.ascii_letters) for _ in range(50))
#包含字母、数字、特殊字符的随机字符串
ran3 = ''.join(random.choice(string.ascii_letters + string.punctuation) for _ in range(51))