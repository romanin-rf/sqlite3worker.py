import os
import sqlite3
from typing import Any, Union, Iterable, Literal, Optional, List, Tuple, Dict
# ! Локальные импорты
try:
	import Units
except:
	from . import Units

class __func__:
	def to_sqltype(tp: Any, primary: bool=False) -> str:
		if tp == int:
			return "INTEGER" + (" PRIMARY KEY" if (primary) else "")
		elif tp == float:
			return "REAL" + (" PRIMARY KEY" if (primary) else "")
		elif tp == str:
			return "TEXT" + (" PRIMARY KEY" if (primary) else "")
		elif tp == bool:
			return "BOOLEAN"
		elif tp == bytes:
			return "BLOB"
		elif tp is None:
			return "NULL"
		else:
			raise TypeError("This type of data is not supported")
	
	def to_pythontype(tp: str) -> Any:
		if tp.upper() in Units.INTEGER:
			return int
		elif tp.upper() in Units.FLOAT:
			return float
		elif tp.upper() in Units.STRING:
			return str
		elif tp.upper() in Units.BOOLEAN:
			return bool
		elif tp.upper() in Units.BYTES:
			return bytes
		else:
			return None

class SQLite3Worker():
	def __init__(
		self,
		path: str,
		check_same_thread: Optional[bool]=None
	) -> None:
		"""Создание файла SQLite3 или открытие существуещего для работы"""
		cst = check_same_thread or False
		self.path = os.path.abspath(path)
		self.db_connect = sqlite3.connect(self.path, check_same_thread=cst)
		self.db_cursor = self.db_connect.cursor()

	def request(
		self,
		request_text: str,
		mode: Optional[Literal["a", "r", "w"]]=None,
		params: Optional[Iterable[Any]]=None
	) -> Optional[List[Tuple]]:
		"""`Функция для запросов` к базе данных SQLite"""
		mode = mode or "a"
		if params is None:
			self.db_cursor.execute(request_text)
		else:
			self.db_cursor.execute(request_text, params)
		if mode == "w":
			self.db_connect.commit()
			out = None
		elif mode == "r":
			out = self.db_cursor.fetchall()
		elif mode == "a":
			self.db_cursor.execute(request_text)
			self.db_connect.commit()
			out = self.db_cursor.fetchall()
		else:
			out = None
		return out

	def table_length(self, table_name: str) -> int:
		return self.request(f"select count(*) from {table_name}", "r")[0][0]

	def create_table(
		self,
		table_name: str,
		colons: Dict[str, Tuple[Any, bool]]
	) -> None:
		"""`Создание таблицы`, ЕСЛИ ЕЁ НЕТУ в базе данных SQLite"""
		colons_list = []
		for i in list(colons.items()):
			colons_list.append(
				"\"{0}\" {1}".format(i[0], __func__.to_sqltype(i[1][0], i[1][1]))
			)
		self.request("CREATE TABLE IF NOT EXISTS \"{0}\" ({1});".format(table_name, ", ".join(colons_list)), "w")

	def get_tables_list(self) -> List[str]:
		"""`Список таблиц` в базе данных SQLite"""
		tables_info, tables_list = self.request("SELECT * FROM sqlite_master WHERE type = 'table';", "r"), []
		for i in tables_info:
			tables_list.append(str(i[1]))
		return tables_list

	def delete_table(self, table_name: str) -> None:
		"""`Удаление таблицы` из базы данных SQLite"""
		self.request(f"DROP TABLE IF EXISTS \"{table_name}\";", "w")

	def get_colons_list(
		self,
		table_name: str
	) -> List[Dict[str, Any]]:
		"""`Возвращает список с информацией о колонках` в таблице базе данных SQLite"""
		colons, colons_list = self.request(f"PRAGMA table_info(\"{table_name}\");", "r"), []
		for i in colons:
			colons_list.append(
				{
					"id": int(i[0]),
					"name": str(i[1]),
					"type": __func__.to_pythontype(str(i[2])),
					"primary": True if (int(i[5]) == 1) else False
				}
			)
		colons_list.sort(key=lambda x: x["id"])
		return colons_list
	
	def get_colons_names(
		self,
		table_name: str
	) -> List[str]:
		"""`Возвращает список с именами колонок` в таблице базе данных SQLite"""
		return [i["name"] for i in self.get_colons_list(table_name)]

	def add_data(self, table_name: str, data: Iterable[Any]) -> None:
		"""`Добавление данных в таблицу` базы данных SQLite"""
		if not isinstance(data, tuple):
			data = tuple(data)
		colons_names = [i["name"] for i in self.get_colons_list(table_name)]
		self.request(
			"INSERT INTO {0} ({1}) VALUES({2});".format(
				table_name,
				",".join(colons_names),
				",".join(["?" for i in range(len(data))])
			),
			"w",
			data
		)
	
	def add_datas(
		self,
		table_name: str,
		data: Iterable[Iterable[Any]]
	) -> None:
		"""`Многократное добавление данных в таблицу` базы данных SQLite"""
		for i in data:
			self.add_data(table_name, i)

	def get_data(
		self,
		table_name: str,
		colon_name: str,
		value: Any
	) -> List[Tuple[Any]]:
		"""`Возращает данные из таблицы` базы данных SQLite"""
		return self.request("SELECT * FROM {0} WHERE {1} = ?;".format(table_name, colon_name), "r", [value])
	
	def get_data_all(self, table_name: str) -> Union[list[tuple[Any]], list]:
		"""`Возращает все данные из таблицы` базы данных SQLite"""
		return self.request(f"SELECT * FROM \"{table_name}\";", "r")
	
	def get_count_data(self, table_name: str) -> int:
		"""`Возращает количество строк в таблице` базы данных SQLite"""
		return self.request(f"SELECT COUNT(*) FROM \"{table_name}\";", "r")[0][0]

	def exists_data(
		self,
		table_name: str,
		colon_name: str,
		value: Any
	) -> Union[Tuple[Literal[False], None], Tuple[Literal[True], list]]:
		"""`Проверяет наличия данных в таблице` базе данных SQLite"""
		data = self.request(f"SELECT * FROM \"{table_name}\" WHERE \"{colon_name}\"= ?;", "r", [value])
		anwer = (len(data) != 0)
		return anwer, (data[0] if (anwer) else None)
	
	def update_data(
		self,
		table_name: str,
		colon_name: str,
		value: Any,
		new_value: Dict[str, Any]
	) -> None:
		"""`Обновляет данные в таблице` базе данных SQLite"""
		invalue = list(new_value.items())
		for i in invalue:
			self.request(
				"UPDATE \"{0}\" SET \"{1}\" = ? where \"{2}\" = ?;".format(
					table_name, i[0], colon_name
				),
				"w",
				[i[1], value]
			)

	def delete_data(self, table_name: str, colon_name: str, value: Any) -> None:
		"""`Удаление данных из таблицы` базы данных SQLite"""
		self.request(f"DELETE FROM {table_name} WHERE {colon_name}= ?;", "w", [value])

	def exists_colon(self, table_name: str, colon_name: str) -> bool:
		"""Проверка наличия `колонки` в таблице базе данных SQLite"""
		cl = self.get_colons_list(table_name)
		for i in cl:
			if i["name"] == colon_name:
				return True
		return False

	def exists_table(self, table_name: str) -> bool:
		"""Проверка наличия `таблицы` базы данных SQLite"""
		return (table_name in self.get_tables_list())
