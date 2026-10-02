import ctypes
import asyncio
import threading
import time
import uuid

from redis import Redis

from backend.config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT
from backend.services.LLMServices import checkLMStudioServerRunning
from backend.services.settingsServices import getMode
from database.index import db


class StartupGuard:
	REDIS_LOCK_KEY = "HUB:LOCK"
	REDIS_LOCK_TTL = 30
	REDIS_HEARTBEAT_INTERVAL = 10
	WINDOWS_MUTEX_NAME = "Global\\HUB_BACKEND_SINGLE_INSTANCE"

	def __init__(self):
		self.instance_id = str(uuid.uuid4())
		self.redis_client = Redis(
			host=REDIS_HOST,
			password=REDIS_PASSWORD,
			port=REDIS_PORT,
			db=0,
			decode_responses=True,
		)
		self.mutex_handle = None
		self.redis_lock_acquired = False
		self.stop_event = threading.Event()
		self.heartbeat_thread = None

	def acquire(self) -> bool:
		while True:
			if not self._acquire_windows_mutex():
				print("[STARTUP] Another HUB instance is already running")
				return False

			try:
				self.redis_client.ping()
				if not self.redis_client.set(
					self.REDIS_LOCK_KEY,
					self.instance_id,
					nx=True,
					ex=self.REDIS_LOCK_TTL,
				):
					print("[STARTUP] Another HUB instance owns the Redis lock")
					self._release_windows_mutex()
					return False

				self.redis_lock_acquired = True
				if not db.init_pool():
					print("[STARTUP] Database is not ready")
					self._release_redis_lock()
					self._release_windows_mutex()
					print("[STARTUP] Retrying activation check in 5 seconds")
					time.sleep(5)
					continue

				if not self._check_llm_server():
					self._release_redis_lock()
					self._release_windows_mutex()
					print("[STARTUP] Retrying activation check in 5 seconds")
					time.sleep(5)
					continue

				self.heartbeat_thread = threading.Thread(
					target=self._redis_lock_heartbeat,
					name="hub-startup-lock-heartbeat",
					daemon=True,
				)
				self.heartbeat_thread.start()
				print(f"[STARTUP] Activation lock acquired: {self.instance_id}")
				return True
			except Exception as error:
				print(f"[STARTUP] Activation check failed: {error}")
				if self.redis_lock_acquired:
					self._release_redis_lock()
				self._release_windows_mutex()
				print("[STARTUP] Retrying activation check in 5 seconds")
				time.sleep(5)

	def release(self):
		self.stop_event.set()

		if self.heartbeat_thread and self.heartbeat_thread is not threading.current_thread():
			self.heartbeat_thread.join(timeout=2)
			self.heartbeat_thread = None

		if self.redis_lock_acquired:
			self._release_redis_lock()

		try:
			self.redis_client.close()
		except Exception as error:
			print(f"[STARTUP] Redis connection close failed: {error}")

		self._release_windows_mutex()

	def _release_redis_lock(self):
		try:
			self.redis_client.eval(
				"""
				if redis.call("GET", KEYS[1]) == ARGV[1] then
					return redis.call("DEL", KEYS[1])
				else
					return 0
				end
				""",
				1,
				self.REDIS_LOCK_KEY,
				self.instance_id,
			)
		except Exception as error:
			print(f"[STARTUP] Redis lock release failed: {error}")
		finally:
			self.redis_lock_acquired = False

	def _check_llm_server(self) -> bool:
		mode_settings = asyncio.run(getMode())
		mode = mode_settings.get("mode", "basic")
		if mode not in ("server", "client"):
			return True

		server_ip = "localhost" if mode == "server" else mode_settings.get("server_ip")
		if mode == "client" and not server_ip:
			print("[STARTUP] Client mode has no LM Studio server IP")
			return False

		is_running = asyncio.run(checkLMStudioServerRunning(server_ip))
		if not is_running:
			print(f"[STARTUP] LM Studio server is not running: {server_ip}")
		return is_running

	def _acquire_windows_mutex(self) -> bool:
		if self.mutex_handle:
			return True

		kernel32 = ctypes.windll.kernel32
		handle = kernel32.CreateMutexW(None, False, self.WINDOWS_MUTEX_NAME)
		if not handle:
			return False

		if kernel32.GetLastError() == 183:
			kernel32.CloseHandle(handle)
			return False

		self.mutex_handle = handle
		return True

	def _release_windows_mutex(self):
		if not self.mutex_handle:
			return

		try:
			ctypes.windll.kernel32.ReleaseMutex(self.mutex_handle)
			ctypes.windll.kernel32.CloseHandle(self.mutex_handle)
		finally:
			self.mutex_handle = None

	def _redis_lock_heartbeat(self):
		while not self.stop_event.wait(self.REDIS_HEARTBEAT_INTERVAL):
			if not self.redis_lock_acquired:
				return

			try:
				result = self.redis_client.eval(
					"""
					if redis.call("GET", KEYS[1]) == ARGV[1] then
						return redis.call("EXPIRE", KEYS[1], ARGV[2])
					else
						return 0
					end
					""",
					1,
					self.REDIS_LOCK_KEY,
					self.instance_id,
					self.REDIS_LOCK_TTL,
				)
				if result == 0:
					print("[STARTUP] Redis activation lock was lost")
					self.redis_lock_acquired = False
					return
			except Exception as error:
				print(f"[STARTUP] Redis lock heartbeat failed: {error}")
