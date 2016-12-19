from rolepermissions.roles import AbstractUserRole

class Student(AbstractUserRole):
	available_permissions = {
	}

class Professor(AbstractUserRole):
	available_permissions = {
	}

class Coordinator(AbstractUserRole):
	available_permissions = {
	}

class SystemAdmin(AbstractUserRole):
	pass
