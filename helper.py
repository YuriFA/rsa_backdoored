import random

def miller_rabin(n):
  if not(n & 1) or n % 3 == 0 or n % 5 == 0 or n % 7 == 0 or n % 11 == 0: return False
  s = 0
  d = n - 1
  while d % 2 == 0:
    d = d >> 1
    s += 1

  for k in range(n.bit_length()):
    a = random.randint(2, n - 2)
    x = pow(a % (n - 1), int(d), n)

    if(x == 1 or x == n - 1):
      continue

    for j in range(s - 1):
      x = (x * x) % n
      if(x == 1):
        return False
      if(x == n - 1):
        break
    else:
      return False

  return True

def gcd(x, y):
  if x == 0:
    return y
  return gcd( y % x, x)

def mmi(a, m):
  '''modular multiplicative inverse
      a*x = 1 (mod m)
      return x
  '''
  t, newt = 0, 1
  r, newr = m, a
  while newr != 0:
    quotient = r // newr
    r, newr = newr, r - quotient * newr
    t, newt = newt, t - quotient * newt
  if r > 1:
    return('a is not invertible')
  if t < 0:
    t += m
  return t

def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m

def coprime(num, not_allowed=[]):
  res = randint_prime(1, num)
  while gcd(num, res) != 1 or res in not_allowed:
    res = randint_prime(1, num)
  return res

def rand_prime(bit_count, not_allowed=[]):
  bit_count -= 1
  rand_num = random.getrandbits(bit_count) | (1 << bit_count)
  while not(miller_rabin(rand_num)) or rand_num in not_allowed:
    rand_num += 1

  return rand_num

def randint_prime(min, max):
  rand_num = random.randint(min, max)
  while not(miller_rabin(rand_num)):
    rand_num = random.randint(min, max)
  return rand_num

def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, x, y = egcd(b % a, a)
        return (g, y - (b // a) * x, x)

#дробь по модулю(num-числитель,denom-знаменатель)
def exponent(num,denom,mod):
    g,a,b=egcd(denom,mod)
    a=a*num
    while a>mod:
        a=a-mod
    return a

def bitlength(x):
    '''
    Calculates the bitlength of x
    '''
    assert x >= 0
    n = 0
    while x > 0:
        n = n+1
        x = x>>1
    return n

def isqrt(n):
    '''
    Calculates the integer square root
    for arbitrary large nonnegative integers
    '''
    if n < 0:
        raise ValueError('square root not defined for negative numbers')

    if n == 0:
        return 0
    a, b = divmod(bitlength(n), 2)
    x = 2**(a+b)
    while True:
        y = (x + n//x)//2
        if y >= x:
            return x
        x = y

def is_perfect_square(n):
    '''
    If n is a perfect square it returns sqrt(n),

    otherwise returns -1
    '''
    h = n & 0xF; #last hexadecimal "digit"

    if h > 9:
        return -1 # return immediately in 6 cases out of 16.

    # Take advantage of Boolean short-circuit evaluation
    if ( h != 2 and h != 3 and h != 5 and h != 6 and h != 7 and h != 8 ):
        # take square root if you must
        t = isqrt(n)
        if t*t == n:
            return t
        else:
            return -1

    return -1