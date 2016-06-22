from functools import partial
from math import sqrt
from helper import rand_prime, randint_prime, mmi, coprime, egcd, exponent
from Crypto.PublicKey import RSA
import sys
import timeit
import gmpy
import backdoor

BIT_COUNT = 1024

#файл с исходным текстом
TEXT_PATH = 'example/text.txt'
#файл с зашифрованным текстом
ENC_PATH = 'example/encrypt.bin'
#файл с зашифрованным текстом 2
SEC_ENC_PATH = 'example/encrypt2.bin'
#файл с расшифрованным
DEC_PATH = 'example/dec_text.txt'

class SimpleRSA():
	def __init__(self, bit_count):
		self.bit_count = bit_count
		self.b_sz = (bit_count + bit_count) // 8
		self.rsa = ''

	def generate_params(self, rsa=None, e=None):
		if not rsa:
			p = rand_prime(self.bit_count)
			q = rand_prime(self.bit_count, not_allowed=[p])
			n = p * q
			# make sure that p is smaller than q
			if p < q:
					(p, q) = (q, p)
		else:
			p, q, n = rsa.p, rsa.q, rsa.n

		t = (p - 1) * (q - 1)
		e = coprime(t, not_allowed=[e])
		d = mmi(e, t)
		self.rsa = RSA.construct((int(n), int(e), int(d), int(p), int(q)))

	def build_keys(self, with_backdoor=False):
		if with_backdoor:
			self.rsa = backdoor.backdoor_rsa(self.bit_count)
		else:
			self.generate_params()
		self.dp = self.rsa.d % (self.rsa.p - 1)
		self.dq = self.rsa.d % (self.rsa.q - 1)
		self.qinv = gmpy.invert(self.rsa.q, self.rsa.p)

	def encrypt(self, text_path, enc_path):
		"""
			считываем с файла текст, и далее поблочно
			строку переводим в байты формата utf-8
			из полученной строки байт получаем некое число
			его шифруем с помощью закрытого ключа и записываем в файл
		"""
		text = ''
		with open(text_path, 'r') as handle:
			for block in iter(partial(handle.read, self.b_sz), ""):
				text += block
		with open(enc_path, 'wb') as handle:
			for i in range(0, len(text), self.b_sz - 1):
				sliced = text[i:i + min(len(text), self.b_sz - 1)].encode()
				enc_block = pow(int.from_bytes(sliced, byteorder='big', signed=False), self.rsa.e, self.rsa.n)
				print(enc_block, enc_block.to_bytes(self.b_sz, byteorder='big'))
				handle.write(enc_block.to_bytes(self.b_sz, byteorder='big'))

	def decrypt(self, enc_path, dec_path):
		"""
			считываем шифр-текст и поблочно
			преобразуем байты в число и дешифруем с помощью открытого ключа
			полученное число преобразуем в байты, получаем строку и записываем в файл
		"""
		dec = ''
		with open(enc_path, 'rb') as handle:
			while True:
				read_block = handle.read(self.b_sz)
				if len(read_block) == 0: break
				enc_block = int.from_bytes(read_block, byteorder='big', signed=False)
				m1 = pow(enc_block, self.dp, self.rsa.p)
				m2 = pow(enc_block, self.dq, self.rsa.q)
				h = (self.qinv * (m1 - m2)) % self.rsa.p
				m = int(m2 + h * self.rsa.q)
				m_b = m.to_bytes((m.bit_length() // 8) + 1, byteorder='big')
				print(m_b)
				dec_block = m_b.decode()
				dec += dec_block
		with open(dec_path, 'w') as handle:
			handle.write(dec)
		return dec

def main():
	rsabd = SimpleRSA(BIT_COUNT)
	rsabd.build_keys(True)
	print(rsabd.rsa.p, rsabd.rsa.q, rsabd.rsa.e, rsabd.rsa.d)
	# rsabd.encrypt(TEXT_PATH, ENC_PATH)
	# print(rsabd.decrypt(ENC_PATH, DEC_PATH))
	backdoor.recover_key(rsabd.rsa.n, BIT_COUNT)

def factoriztion(n):
	for i in range(int(sqrt(n) + 1), n):
		t = sqrt(pow(i, 2) - n)
		if t%1==0:
			return i+t, i-t
	else:
		return None

def decrypt_repeat(n, e, enc_path, dec_path):
	dec = ''
	b_sz = (BIT_COUNT + BIT_COUNT) // 8
	with open(enc_path, 'rb') as handle:
		while True:
			read_block = handle.read(b_sz)
			if len(read_block) == 0: break
			enc_block = int.from_bytes(read_block, byteorder='big', signed=False)
			x = repeat_attack(enc_block, n, e)
			x_b = x.to_bytes((x.bit_length() // 8) + 1, byteorder='big')
			dec_block = x_b.decode()
			dec += dec_block
	with open(dec_path, 'w') as handle:
		handle.write(dec)
	return dec

def repeat_attack(y, n, e):
	new_y = pow(y, e, n)
	while new_y != y:
		old_y = new_y
		new_y = pow(new_y, e, n)
	return old_y

def do_repeat_attack():
	rsa_o = SimpleRSA(BIT_COUNT)
	rsa_o.build_keys()
	print(rsa_o.rsa.p, rsa_o.rsa.q)
	rsa_o.encrypt(TEXT_PATH, ENC_PATH)
	print(decrypt_repeat(rsa_o.rsa.n, rsa_o.rsa.e, ENC_PATH, DEC_PATH))

def do_factorization():
	print(factoriztion(153649*152041))
	print(factoriztion(23360947609))

def do_without_keys():
	rsa_f = SimpleRSA(BIT_COUNT)
	rsa_f.generate_params()
	rsa_s = SimpleRSA(BIT_COUNT)
	rsa_s.generate_params(rsa_f.rsa, rsa_f.rsa.e)
	print('N: ',rsa_f.rsa.n, rsa_s.rsa.n)
	print('e первого: ',rsa_f.rsa.e,'e второго: ',rsa_s.rsa.e)
	#шифруем одно сообщение два раза
	rsa_f.encrypt(TEXT_PATH, ENC_PATH)
	rsa_s.encrypt(TEXT_PATH, SEC_ENC_PATH)
	print(decrypt_without_keys(rsa_f.rsa.n, rsa_f.rsa.e, rsa_s.rsa.e, ENC_PATH, SEC_ENC_PATH))

def decrypt_without_keys(n, e1, e2, enc_path1, enc_path2):
	b_sz = (BIT_COUNT + BIT_COUNT) // 8
	g, r, s = egcd(e1, e2)
	dec = ''
	with open(enc_path1, 'rb') as handle:
		f_enc = handle.read()
	with open(enc_path2, 'rb') as handle:
		s_enc = handle.read()

	for i in range(0, len(f_enc), b_sz):
		sliced_f = f_enc[i:i + min(len(f_enc), b_sz)]
		sliced_s = s_enc[i:i + min(len(s_enc), b_sz)]
		y1 = int.from_bytes(sliced_f, byteorder='big', signed=False)
		y2 = int.from_bytes(sliced_s, byteorder='big', signed=False)
		print(sliced_f, y1)
		print(sliced_s, y2)
		if r < s:
			r,s,y1,y2 = s,r,y2,y1
		print(r,s,y1,y2)
		if s < 0:
			s = -s
		yr = pow(y1, r, n)
		ys = pow(y2, s, n)
		result = int(yr // ys + exponent(yr % ys, ys, n)) % n
		res_b = result.to_bytes((result.bit_length() // 8) + 1, byteorder='big')
		dec += res_b.decode()
	return dec

if __name__ == '__main__':
	sys.exit(main())
	# sys.exit(do_repeat_attack())
	# sys.exit(do_without_keys())
	# sys.exit(do_factorization())
