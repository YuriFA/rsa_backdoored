from functools import partial
import sys
import timeit
import gmpy
import backdoor

BIT_COUNT = 2048

#файл с исходным текст
TEXT_PATH = 'text.txt'
#файл с зашифрованным текстом
ENC_PATH = 'encrypt.bin'
#файл с расшифрованным
DEC_PATH = 'dec_text.txt'

class RSABD():
	def __init__(self, bit_count):
		#save block size
		self.b_sz = (bit_count + bit_count) // 8
		self.rsa = backdoor.backdoor_rsa()
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
		with open(enc_path, 'wb+') as handle:
			for i in range(0, len(text), self.b_sz - 1):
				sliced = text[i:i + min(len(text), self.b_sz - 1)].encode()
				enc_block = pow(int.from_bytes(sliced, byteorder='big', signed=False), self.rsa.e, self.rsa.n)
				print(enc_block.to_bytes(self.b_sz, byteorder='big'))
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
				dec_block = m.to_bytes((m.bit_length() // 8) + 1, byteorder='big').decode()
				dec += dec_block
		with open(dec_path, 'w') as handle:
			handle.write(dec)
		return dec

def main():
	rsa = RSABD(BIT_COUNT)
	rsa.encrypt(TEXT_PATH, ENC_PATH)
	print(rsa.decrypt(ENC_PATH, DEC_PATH))
if __name__ == '__main__':
	sys.exit(main())
