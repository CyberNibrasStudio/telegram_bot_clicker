import sqlite3


class BotDB:

	def __init__(self, db_file):
		#инициализация с бд
		self.conn = sqlite3.connect(db_file, check_same_thread=False)
		self.cursor = self.conn.cursor()
	
	def user_exists(self, user_id):
		#проверка есть ли юзер в бд
		result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", [user_id])
		return bool(len(result.fetchall()))
		
	def get_user_id(self, user_id):
		#получаем айди юзера по его user_id в телеграм
		result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
		return result.fetchone()[0]
		
	def get_users(self):
		#получаем айди юзера по его user_id в телеграм
		result = self.cursor.execute("SELECT `user_id` FROM `users`")
		return result.fetchone()
		
	def add_user(self, user_id, plusmoney, money, moneyR):
		#добавление юзера в бд
		self.cursor.execute("INSERT INTO `users` (`user_id`, `plusmoney`, `money`, `moneyR`) VALUES (?, ?, ?, ?)", (user_id, plusmoney, money, moneyR))
		return self.conn.commit()
		
	def get_records(self, user_id):
		#подучение записи
		result = self.cursor.execute("SELECT * FROM `users` WHERE `user_id` = ?",[user_id])
		return result.fetchone()
		
	def get_passive(self):
		#подучение записи
		result = self.cursor.execute("SELECT `user_id`, `passive`, `money` FROM `users` WHERE `passive` > '0'")
		return result.fetchall()
		
	def update_money(self, user_id, money):
		self.cursor.execute("UPDATE `users` SET `money` = ? WHERE `user_id` = ?",[money, user_id])
		return self.conn.commit()
		
	def update_moneyR(self, user_id, moneyR):
		self.cursor.execute("UPDATE `users` SET `moneyR` = ? WHERE `user_id` = ?",[moneyR, user_id])
		return self.conn.commit()
		
	def update_plusmoney(self, user_id, plusmoney):
		self.cursor.execute("UPDATE `users` SET `plusmoney` = ? WHERE `user_id` = ?",[plusmoney, user_id])
		return self.conn.commit()
		
	def update_passive(self, user_id, passive):
		self.cursor.execute("UPDATE `users` SET `passive` = ? WHERE `user_id` = ?",[passive, user_id])
		return self.conn.commit()
		
	def add_payments(self, user_id, amount, payment, comment, date):
		#добавление записи
		self.cursor.execute("INSERT INTO `payments` (`user_id`, `amount`, `payment`, `comment`, `date`) VALUES (?, ?, ?, ?, ?)",(user_id, amount, payment, comment, date))
		return self.conn.commit()
		
	def delete_payments(self, user_id, comment):
		self.cursor.execute("DELETE FROM `payments` WHERE `user_id` = ? AND `comment` = ?", [user_id, comment])
		return self.conn.commit()
		
	def get_payments(self, user_id, payment):
		#подучение записи
		result = self.cursor.execute("SELECT * FROM `payments` WHERE `user_id` = ? AND `payment` = ?",[user_id, payment])
		return result.fetchone()
		
	def close(self):
		#закрытие соединения базы данных
		self.conn.close()