from  redis import StrictRedis

sr = StrictRedis()
sr.set('laowang', 'mimizhang')
sr.get('laowang')
print(sr.get('laowang'))
